# python3 /path/to/text-preprocessing/main.py --input_json /path/to/text-preprocessing/input.json

from graph_rag import custom_embedder, custom_llm
import json
import os
import chunk_getter
import argparse
from llama_index.core import PropertyGraphIndex
from fact_checker import checker
from llama_index.core.postprocessor import LLMRerank
from llama_index.core.prompts import PromptTemplate
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

    if os.path.exists('data') and os.path.exists('plugins'):
        graph_index = PropertyGraphIndex.from_existing(
            llm=custom_llm,
            property_graph_store=graph_store,
            embed_model=custom_embedder,
            include_embeddings=True,
        )
    else:
        graph_index = PropertyGraphIndex(
            nodes=nodes,
            llm=custom_llm,
            property_graph_store=graph_store,
            embed_model=custom_embedder,
            include_embeddings=True,
        )

    retriever = graph_index.as_retriever(
        include_text=True,
        similarity_top_k=30
    )

    prompt_str = (
        "A list of documents is shown below. Each document has a number next to it along "
        "with a summary of the document. A question is also provided. \n"
        "Respond with the numbers of the documents "
        "you should consult to answer the question, in order of relevance, as well \n"
        "as the relevance score. The relevance score is a number from 1-10 based on "
        "how relevant you think the document is to the question.\n"
        "If some documents contain conflicting or contradictory information relevant to the question, "
        "assign relevance scores in a balanced way that fairly represents the differing viewpoints "
        "or data, so conflicting evidence is not overshadowed by other documents.\n"
        "Do not include any documents that are not relevant to the question. \n"
        "Example format: \n"
        "Document 1:\n<summary of document 1>\n\n"
        "Document 2:\n<summary of document 2>\n\n"
        "...\n\n"
        "Document 10:\n<summary of document 10>\n\n"
        "Question: <question>\n"
        "Answer:\n"
        "Doc: 9, Relevance: 7\n"
        "Doc: 3, Relevance: 4\n"
        "Doc: 7, Relevance: 3\n\n"
        "Let's try this now: \n\n"
        "{context_str}\n"
        "Question: {query_str}\n"
        "Answer:\n"
    )

    custom_choice_template = PromptTemplate(
        template=prompt_str
    )

    reranker = LLMRerank(
        llm=custom_llm,
        choice_batch_size=5,
        top_n=3,
        choice_select_prompt=custom_choice_template
    )

    query_engine = graph_index.as_query_engine(
        llm=custom_llm,
        include_text=True,
        similarity_top_k=3,
        node_postprocessors=[reranker],
        postprocessors=[retriever],
    )

    response = query_engine.query(data.input_promt)

    facts = []
    facts.append(response.response)

    result = checker.check_facts(data.input_promt, facts)
    print(result)

if __name__ == '__main__':
    main()
