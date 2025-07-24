from vector_rag import custom_embedder, custom_llm, get_retrieved_nodes
import json
import chunk_getter
import argparse
from fact_checker import checker
from llama_index.core import VectorStoreIndex as Index  # Renamed to avoid unused import
import time

def main():
    parser = argparse.ArgumentParser(description="Vector RAG-based fact checking")
    parser.add_argument("--input_json", type=str, help="Path to input json")
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

    # Создаем векторный индекс
    index = Index(  # Using renamed import
        nodes=nodes,
        llm=custom_llm,
        embed_model=custom_embedder,
        include_embeddings=True,
    )

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