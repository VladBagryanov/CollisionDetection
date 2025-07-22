from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.llms import CustomLLM, LLMMetadata, CompletionResponse
import requests

folder_id = ""
iam_token=""

LLM_URI="https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
EMB_URL="https://llm.api.cloud.yandex.net/foundationModels/v1/textEmbedding"

class CustomEmbeddingModel(BaseEmbedding):
    def __init__(self):
        super().__init__(model_name="custom_embedder")

    def _get_query_embedding(self, query: str) -> list[float]:
        data = {}
        data["modelUri"] = f"emb://{folder_id}/text-search-doc/latest"
        data["text"] = query
        response = requests.post(
            EMB_URL,
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {iam_token}"
            },
            json=data,
        )
        return response.json()["embedding"]
    
    async def _aget_query_embedding(self, query: str) -> list[float]:
        data = {}
        data["modelUri"] = f"emb://{folder_id}/text-search-doc/latest"
        data["text"] = query
        response = requests.post(
            EMB_URL,
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {iam_token}"
            },
            json=data,
        )
        return await response.json()["embedding"]

    def _get_text_embedding(self, text: str) -> list[float]:
        data = {}
        data["modelUri"] = f"emb://{folder_id}/text-search-doc/latest"
        data["text"] = text
        response = requests.post(
            EMB_URL,
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {iam_token}"
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
        data["modelUri"] = f"gpt://{folder_id}/yandexgpt-lite"
        data["completionOptions"] = {"temperature": 0.3, "maxTokens": 1000}
        data["messages"] = [
            {"role": "user", "text": f"{prompt}"},
        ]
        
        response = requests.post(
            LLM_URI,
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {iam_token}"
            },
            json=data,
        )
        return CompletionResponse(text=response.json()["result"]["alternatives"][0]["message"]["text"])

    @property
    def metadata(self):
        return LLMMetadata()
    
    def stream_complete(self, prompt, formatted, **kwargs):
        data = {}
        data["modelUri"] = f"gpt://{folder_id}/yandexgpt-lite"
        data["completionOptions"] = {"temperature": 0.3, "maxTokens": 1000}
        data["messages"] = [
            {"role": "user", "text": f"{prompt}"},
        ]
        
        response = requests.post(
            LLM_URI,
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {iam_token}"
            },
            json=data,
        )
        yield CompletionResponse(text=response.json()["result"]["alternatives"][0]["message"]["text"])
