from typing import Optional
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
import requests
import aiohttp

class YandexCloudLLM:
    """
    Сервис для работы с LLM через Yandex Cloud API,
    используя интерфейс OpenAI.
    """
    
    def __init__(
        self,
        api_key: str,
        folder_id: str,
        model_url: str = None,
        model_uri: str = "llama-lite",
        model_type: str = "gpt",
        temperature: float = 0.1,
        max_tokens: int = 1000,
        timeout: int = 30
    ):
        """
        Инициализация клиента Yandex Cloud LLM.
        
        Args:
            api_key: API ключ Yandex Cloud
            folder_id: Идентификатор каталога
            model_uri: URI модели (например, "llama-lite")
            temperature: Температура генерации (0-1)
            max_tokens: Максимальное количество токенов
            timeout: Таймаут запроса в секундах
        """
        self.api_key=api_key
        if model_url:
            self.model_url = model_url
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://llm.api.cloud.yandex.net/v1"
        )
        
        self.model = f"{model_type}://{folder_id}/{model_uri}/latest"
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout

    @retry(
        stop=stop_after_attempt(1),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def analyze_consistency(
        self,
        prompt: str,
        system_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Анализ согласованности текста с помощью LLM.
        
        Args:
            prompt: Промпт для модели
            temperature: Переопределение температуры (опционально)
            max_tokens: Переопределение максимального количества токенов (опционально)
        
        Returns:
            Структурированный ответ модели
        
        Raises:
            ValueError: При ошибке парсинга ответа
            Exception: При других ошибках API
        """
        try:
            # Создаем запрос к API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
                timeout=self.timeout
            )
            
            result = response.choices[0].message.content

            return result
            
        except Exception as e:
            print(f"Ошибка при запросе к LLM API: {str(e)}")
            raise

    def request_gpt(
        self,
        prompt: str,
        system_prompt: str = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        data = {}
        data["modelUri"] = self.model
        data["completionOptions"] = {"temperature": temperature, "maxTokens": max_tokens}
        data["messages"] = []
        if (system_prompt != None):
            data["messages"].append({"role": "system", "text": system_prompt})
        data["messages"].append({"role": "user", "text": prompt})
        
        try:
            response = requests.post(
                self.model_url,
                headers={
                    "Accept": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                },
                json=data,
            )
            result = response.json()["result"]["alternatives"]
            assert len(result) != 0, "error"
            return result[0]["message"]["text"]
        except Exception as e:
            print(f"Ошибка при запросе к LLM API: {str(e)}")
            raise

    def request_emb(
        self,
        text: str = None
    ) -> str:
        try:
            data = {}
            data["modelUri"] = self.model
            data["text"] = text
            response = requests.post(
                self.model_url,
                headers={
                    "Accept": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                },
                json=data,
            )
            return response.json()["embedding"]
        except Exception as e:
            print(f"Ошибка при запросе к LLM API: {str(e)}")
            raise

    async def request_gpt_async(
        self,
        prompt: str,
        system_prompt: str = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        data = {}
        data["modelUri"] = self.model
        data["completionOptions"] = {"temperature": temperature, "maxTokens": max_tokens}
        data["messages"] = []
        if (system_prompt != None):
            data["messages"].append({"role": "system", "text": system_prompt})
        data["messages"].append({"role": "user", "text": prompt})
        
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(self.model_url, headers=headers, json=data) as resp:
                if resp.status == 200:
                    data = await resp.json()
                else:
                    text = await resp.text()
                    print("error:", text)
                result = data["result"]["alternatives"]
                assert len(result) != 0, "error"
                return result[0]["message"]["text"]
