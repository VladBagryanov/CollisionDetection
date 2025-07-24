from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.llms import CustomLLM, LLMMetadata, CompletionResponse
from yandex_cloud_ml_sdk import YCloudML
from llm_service import YandexCloudLLM
import tokens
from llama_index.core.llms.callbacks import (
    llm_completion_callback,
)
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core import QueryBundle, VectorStoreIndex

EMB_URL="https://llm.api.cloud.yandex.net/foundationModels/v1/textEmbedding"
GPT_URL="https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

emb_model = YandexCloudLLM(tokens.AUTH_TOKEN, tokens.FOLDER_ID, EMB_URL, "text-search-doc", "emb")
rag_model = YandexCloudLLM(tokens.AUTH_TOKEN, tokens.FOLDER_ID, GPT_URL, "yandexgpt-lite")

class CustomEmbeddingModel(BaseEmbedding):
    def __init__(self):
        super().__init__(model_name="custom_embedder")

    def _get_query_embedding(self, query: str) -> list[float]:
        print("get emb")
        ans = emb_model.request_emb(query)
        return ans

    async def _aget_query_embedding(self, query: str) -> list[float]:
        return self._get_query_embedding(query)

    def _get_text_embedding(self, text: str) -> list[float]:
        print("get text")
        ans = emb_model.request_emb(text)
        return ans

class CustomLLMAPI(CustomLLM):
    def __init__(self):
        super().__init__()

    def complete(self, prompt: str, **kwargs) -> CompletionResponse:
        ans = rag_model.request_gpt(prompt)
        print("complete")
        return CompletionResponse(text=ans)
    
    @llm_completion_callback()
    async def acomplete(
        self, prompt: str, formatted: bool = False, **kwargs
    ) -> CompletionResponse:
        print("acomplete")
        res = await rag_model.request_gpt_async(prompt)
        return CompletionResponse(text=res)

    @property
    def metadata(self):
        return LLMMetadata()

    def stream_complete(self, prompt, formatted, **kwargs):
        print("stream complete")
        ans = rag_model.request_gpt(prompt)
        yield CompletionResponse(text=ans)

custom_embedder = CustomEmbeddingModel()
custom_llm = CustomLLMAPI()

def get_retrieved_nodes(
    index: "VectorStoreIndex", custom_llm, custom_embedder, query_str, vector_top_k=10, reranker_top_n=3, with_reranker=False
):
    """
    Получение релевантных документов с помощью векторного поиска.
    Сохраняет тот же интерфейс, что и графовый RAG для совместимости.
    """
    from llama_index.core import VectorStoreIndex  # Import where used
    query_bundle = QueryBundle(query_str)

    # Создаем векторный retriever
    retriever = VectorIndexRetriever(
        index=index,
        similarity_top_k=vector_top_k,
    )

    # Получаем документы
    retrieved_nodes = retriever.retrieve(query_bundle)

    # Если нужно переранжирование, используем тот же reranker что и в графовом RAG
    if with_reranker:
        from llama_index.core.postprocessor import LLMRerank
        from llama_index.core.prompts import PromptTemplate

        prompt_str = (
            "A list of documents is shown below. Each document has a number next to it along with a summary of the document. A question is also provided. \n"
            "Respond with the numbers of the documents you should consult to answer the question, in order of relevance, as well as the relevance score. The relevance score is a number from 1-10 based on how relevant you think the document is to the question.\n"
            "Prioritize documents based on their relevance to the question, regardless of whether they support or contradict the query. Both confirming and contradicting facts are considered equally relevant if they provide significant information, context, or arguments related to the question.\n"
            "Assign relevance scores in a balanced way to fairly represent differing viewpoints or data, ensuring that conflicting evidence is not overshadowed by other documents.\n"
            "Always include at least one document in the response, selecting the most relevant documents even if the relevance is low.\n"
            "Do not include documents that are irrelevant to the question.\n"
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
            top_n=reranker_top_n,
            choice_select_prompt=custom_choice_template
        )

        retrieved_nodes = reranker.postprocess_nodes(retrieved_nodes, query_bundle)

    return retrieved_nodes 