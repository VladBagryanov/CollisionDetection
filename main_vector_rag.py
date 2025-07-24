from vector_rag import custom_embedder, custom_llm, get_retrieved_nodes
import json
import chunk_getter
import argparse
from fact_checker import checker
from llama_index.core import VectorStoreIndex as Index
from llama_index.core import StorageContext
from llama_index.storage.docstore import SimpleDocumentStore
from llama_index.storage.index_store import SimpleIndexStore
from llama_index.vector_stores.simple import SimpleVectorStore
import time

# Параметры подключения к Neo4j
NEO4J_URL = "bolt://localhost:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "supersecret123"

def main():
    parser = argparse.ArgumentParser(description="Vector RAG-based fact checking")
    parser.add_argument("--input_json", type=str, help="Path to input json")
    parser.add_argument("--has_index", type=bool, default=False, help="Exist index")
    args = parser.parse_args()

    # Загружаем данные
    with open(args.input_json, "r") as file:
        input_json = json.load(file)
        data = chunk_getter.Data(
            input_json["conflict"],
            input_json["data_path"],
            chunker=input_json["chunker"]
        )

    # Получаем ноды из документов
    nodes = data.node_getter()

    # Создаем или загружаем индекс
    if args.has_index:
        # Загружаем существующий индекс
        storage_context = StorageContext.from_defaults(
            docstore=SimpleDocumentStore.from_persist_dir("./storage", url=NEO4J_URL, username=NEO4J_USERNAME, password=NEO4J_PASSWORD),
            vector_store=SimpleVectorStore.from_persist_dir("./storage", url=NEO4J_URL, username=NEO4J_USERNAME, password=NEO4J_PASSWORD),
            index_store=SimpleIndexStore.from_persist_dir("./storage", url=NEO4J_URL, username=NEO4J_USERNAME, password=NEO4J_PASSWORD),
        )
        index = Index.from_storage_context(
            storage_context=storage_context,
            llm=custom_llm,
            embed_model=custom_embedder,
            include_embeddings=True,
        )
    else:
        # Создаем новый индекс
        storage_context = StorageContext.from_defaults(
            docstore=SimpleDocumentStore(url=NEO4J_URL, username=NEO4J_USERNAME, password=NEO4J_PASSWORD),
            vector_store=SimpleVectorStore(url=NEO4J_URL, username=NEO4J_USERNAME, password=NEO4J_PASSWORD),
            index_store=SimpleIndexStore(url=NEO4J_URL, username=NEO4J_USERNAME, password=NEO4J_PASSWORD),
        )
        index = Index(
            nodes=nodes,
            storage_context=storage_context,
            llm=custom_llm,
            embed_model=custom_embedder,
            include_embeddings=True,
        )
        # Сохраняем индекс
        index.storage_context.persist("./storage")

    # Получаем релевантные документы
    retrieved_nodes = get_retrieved_nodes(
        index,
        custom_llm,
        custom_embedder,
        data.input_promt,
        vector_top_k=30,
        reranker_top_n=5,
        with_reranker=True
    )

    # Извлекаем тексты из найденных документов
    facts = []
    for node in retrieved_nodes:
        text = str(node.node.get_text())
        facts.append(text)

    # Проверяем факты
    result = checker.check_facts(data.input_promt, facts)
    print(result)

if __name__ == '__main__':
    start_time = time.time()
    main()
    end_time = time.time()
    execution_time_seconds = end_time - start_time
    execution_time_minutes = execution_time_seconds / 60
    print(f"Выполнено за {execution_time_minutes:.2f} минут") 