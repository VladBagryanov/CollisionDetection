from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.llms import CustomLLM, LLMMetadata, CompletionResponse
from yandex_cloud_ml_sdk import YCloudML
from llm_service import YandexCloudLLM
import tokens
from llama_index.core.llms.callbacks import (
    llm_completion_callback,
)

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
