# python3 /path/to/text-preprocessing/main.py --input_json /path/to/text-preprocessing/input.json
from graph_rag import custom_embedder, custom_llm
import json
import chunk_getter
import argparse
from llama_index.core import PropertyGraphIndex
from llama_index.graph_stores.neo4j import Neo4jPGStore

def main():
    parser = argparse.ArgumentParser(description="Collision detection.")
    parser.add_argument("--input_json", type=str, help="Path to input json")

    args = parser.parse_args()

    with open(args.input_json, "r") as file:
        input_json = json.load(file)
        data = chunk_getter.Data(input_json["conflict"], input_json["data_path"], chunker=input_json["chunker"])

    nodes = data.node_getter()

    graph_store = Neo4jPGStore(url="bolt://localhost:7687", username="neo4j", password="supersecret123")
    graph_index = PropertyGraphIndex(
        nodes=nodes,
        llm=custom_llm,
        property_graph_store=graph_store,
        embed_model=custom_embedder,
        include_embeddings=True,
    )
    query_engine = graph_index.as_query_engine(llm=custom_llm)
    response = query_engine.query("What is the name the African bush elephant?")
    print(response)

if __name__ == '__main__':
    main()
