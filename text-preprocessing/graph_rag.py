from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.llms import CustomLLM, LLMMetadata, CompletionResponse
import requests
import tokens

EMB_URL="https://llm.api.cloud.yandex.net/foundationModels/v1/textEmbedding"
LLM_URI="https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

class CustomEmbeddingModel(BaseEmbedding):
    def __init__(self):
        super().__init__(model_name="custom_embedder")

    def _get_query_embedding(self, query: str) -> list[float]:
        data = {}
        data["modelUri"] = f"emb://{tokens.FOLDER_ID}/text-search-doc/latest"
        data["text"] = query
        response = requests.post(
            EMB_URL,
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {tokens.AUTH_TOKEN}"
            },
            json=data,
        )
        return response.json()["embedding"]

    async def _aget_query_embedding(self, query: str) -> list[float]:
        return self._get_query_embedding(query)

    def _get_text_embedding(self, text: str) -> list[float]:
        data = {}
        data["modelUri"] = f"emb://{tokens.FOLDER_ID}/text-search-doc/latest"
        data["text"] = text
        response = requests.post(
            EMB_URL,
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {tokens.AUTH_TOKEN}"
            },
            json=data,
        )
        return response.json()["embedding"]

LLM_URI="https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

class CustomLLMAPI(CustomLLM):
    def __init__(self):
        super().__init__()

    def complete(self, prompt: str, **kwargs) -> CompletionResponse:
        
        data = {}
        data["modelUri"] = f"gpt://{tokens.FOLDER_ID}/yandexgpt-lite"
        data["completionOptions"] = {"temperature": 0.3, "maxTokens": 1000}
        data["messages"] = [
            {"role": "user", "text": f"{prompt}"},
        ]

        response = requests.post(
            LLM_URI,
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {tokens.AUTH_TOKEN}"
            },
            json=data,
        )
        return CompletionResponse(text=response.json()["result"]["alternatives"][0]["message"]["text"])

    @property
    def metadata(self):
        return LLMMetadata()
    
    def stream_complete(self, prompt, formatted, **kwargs):
        data = {}
        data["modelUri"] = f"gpt://{tokens.FOLDER_ID}/yandexgpt-lite"
        data["completionOptions"] = {"temperature": 0.3, "maxTokens": 1000}
        data["messages"] = [
            {"role": "user", "text": f"{prompt}"},
        ]

        response = requests.post(
            LLM_URI,
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {tokens.AUTH_TOKEN}"
            },
            json=data,
        )
        yield CompletionResponse(text=response.json()["result"]["alternatives"][0]["message"]["text"])

custom_embedder = CustomEmbeddingModel()
custom_llm = CustomLLMAPI()
