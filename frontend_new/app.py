#!/usr/bin/env python3
"""
Flask API сервер для frontend интерфейса поиска в документации
"""

import sys
import os
import json
import time
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import subprocess
import threading
import queue

# Добавляем путь к основному проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Импортируем модули из основного проекта
try:
    from chunk_getter import Data
    from fact_checker_new import searcher
    from graph_rag import custom_embedder, custom_llm
    from llama_index.core import PropertyGraphIndex
    from llama_index.core.retrievers import VectorContextRetriever, LLMSynonymRetriever
    from llama_index.core import QueryBundle
    from llama_index.core.postprocessor import LLMRerank
    from llama_index.core.prompts import PromptTemplate
    from llama_index.graph_stores.neo4j import Neo4jPGStore
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    print("Убедитесь, что все зависимости установлены и Neo4j запущен")
    sys.exit(1)

app = Flask(__name__)
CORS(app)

# Глобальные переменные для кэширования
graph_index = None
graph_store = None

def get_retrieved_nodes(
    index, custom_llm, custom_embedder, query_str, vector_top_k=10, reranker_top_n=3, with_reranker=False
):
    """Получение релевантных узлов из графа"""
    query_bundle = QueryBundle(query_str)

    syn = LLMSynonymRetriever(
        graph_store=index.property_graph_store,
        llm=custom_llm,
        include_text=True,
        max_keywords=8,
        path_depth=5
    )

    vec = VectorContextRetriever(
        graph_store=index.property_graph_store,
        vector_store=index.vector_store,
        embed_model=custom_embedder,
        include_text=True,
        similarity_top_k=vector_top_k,
        path_depth=5
    )

    retriever = index.as_retriever(sub_retrievers=[syn, vec], include_text=True)
    retrieved_nodes = retriever.retrieve(query_bundle)
    
    if with_reranker:
        prompt_str = (
            "Ниже показан список внутренних документов компании. Каждый документ имеет номер и краткое описание. "
            "Также предоставлен вопрос сотрудника.\n"
            "Ответьте номерами документов, которые нужно изучить для ответа на вопрос сотрудника, "
            "в порядке релевантности, а также оценкой релевантности от 1 до 10.\n"
            "Приоритизируйте документы на основе их релевантности к вопросу сотрудника.\n"
            "Всегда включите хотя бы один документ в ответ, выбрав наиболее релевантные документы.\n"
            "Не включайте документы, не относящиеся к вопросу сотрудника.\n"
            "Формат ответа:\n"
            "Документ 1:\n<описание документа 1>\n\n"
            "Документ 2:\n<описание документа 2>\n\n"
            "...\n\n"
            "Документ 10:\n<описание документа 10>\n\n"
            "Вопрос сотрудника: <вопрос>\n"
            "Ответ:\n"
            "Док: 9, Релевантность: 7\n"
            "Док: 3, Релевантность: 4\n"
            "Док: 7, Релевантность: 3\n\n"
            "Попробуем сейчас:\n\n"
            "{context_str}\n"
            "Вопрос сотрудника: {query_str}\n"
            "Ответ:\n"
        )

        custom_choice_template = PromptTemplate(template=prompt_str)
        reranker = LLMRerank(
            llm=custom_llm,
            choice_batch_size=5,
            top_n=reranker_top_n,
            choice_select_prompt=custom_choice_template
        )
        retrieved_nodes = reranker.postprocess_nodes(retrieved_nodes, query_bundle)
    
    return retrieved_nodes

def initialize_graph():
    """Инициализация графа знаний"""
    global graph_index, graph_store
    
    try:
        print("Инициализация графа знаний...")
        graph_store = Neo4jPGStore(
            url="bolt://localhost:7687", 
            username="neo4j", 
            password="enrico-cecilia-cable-uranium-twin-190"
        )
        
        # Пытаемся загрузить существующий граф
        try:
            graph_index = PropertyGraphIndex.from_existing(
                llm=custom_llm,
                property_graph_store=graph_store,
                embed_model=custom_embedder,
                include_embeddings=True,
            )
            print("Граф успешно загружен из существующих данных")
        except Exception as e:
            print(f"Не удалось загрузить существующий граф: {e}")
            print("Создание нового графа...")
            
            # Создаем новый граф
            data = Data("", "input_data", chunker="basic")
            nodes = data.node_getter()
            
            graph_index = PropertyGraphIndex(
                nodes=nodes,
                llm=custom_llm,
                property_graph_store=graph_store,
                embed_model=custom_embedder,
                include_embeddings=True,
            )
            print("Новый граф создан успешно")
            
    except Exception as e:
        print(f"Ошибка инициализации графа: {e}")
        graph_index = None

@app.route('/')
def index():
    """Главная страница"""
    return send_from_directory('.', 'index.html')

@app.route('/api/search', methods=['POST'])
def search():
    """API endpoint для поиска в документах"""
    try:
        data = request.get_json()
        question = data.get('question', '')
        data_path = data.get('data_path', 'input_data')
        chunker = data.get('chunker', 'basic')
        
        if not question:
            return jsonify({'error': 'Вопрос не может быть пустым'}), 400
        
        print(f"Получен запрос на поиск: {question}")
        
        # Проверяем, инициализирован ли граф
        if graph_index is None:
            return jsonify({
                'error': 'Граф знаний не инициализирован. Убедитесь, что Neo4j запущен и доступен.'
            }), 500
        
        # Получаем релевантные документы
        print("Поиск релевантных документов...")
        retrieved_nodes = get_retrieved_nodes(
            graph_index, custom_llm, custom_embedder, question, 
            vector_top_k=20, reranker_top_n=5, with_reranker=True
        )
        
        # Извлекаем текст документов с метаданными
        documents_with_metadata = []
        for i, node in enumerate(retrieved_nodes):
            text = str(node.node.get_text())
            metadata = node.node.metadata if hasattr(node.node, 'metadata') else {}
            source_metadata = node.node.source_node.metadata if hasattr(node.node, 'source_node') and hasattr(node.node.source_node, 'metadata') else {}
            combined_metadata = {**metadata, **source_metadata}
            
            documents_with_metadata.append({
                'text': text,
                'metadata': combined_metadata,
                'node_id': node.node.id_ if hasattr(node.node, 'id_') else None
            })
        
        # Ищем ответ в документах
        print("Поиск ответа в документах...")
        result = searcher.search_documents(question, documents_with_metadata)
        
        # Преобразуем результат в JSON-совместимый формат
        response_data = {
            'answer': result.answer,
            'found_information': result.found_information,
            'sources': result.sources,
            'confidence': result.confidence
        }
        
        print(f"Поиск завершен. Найдено источников: {len(result.sources)}")
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Ошибка при поиске: {str(e)}")
        return jsonify({
            'error': f'Ошибка при поиске: {str(e)}'
        }), 500

@app.route('/api/status', methods=['GET'])
def status():
    """Проверка статуса сервера"""
    return jsonify({
        'status': 'ok',
        'graph_initialized': graph_index is not None,
        'neo4j_connected': graph_store is not None
    })

@app.route('/api/init', methods=['POST'])
def init_graph():
    """Принудительная инициализация графа"""
    try:
        initialize_graph()
        return jsonify({
            'status': 'success',
            'message': 'Граф инициализирован успешно'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Ошибка инициализации: {str(e)}'
        }), 500

if __name__ == '__main__':
    print("Запуск Flask сервера...")
    print("Инициализация графа знаний...")
    
    # Инициализируем граф в отдельном потоке
    def init_graph_thread():
        initialize_graph()
    
    thread = threading.Thread(target=init_graph_thread)
    thread.daemon = True
    thread.start()
    
    print("Сервер запущен на http://localhost:5000")
    print("Откройте http://localhost:5000 в браузере")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
