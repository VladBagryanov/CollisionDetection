from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
import logging
from pathlib import Path
import json

@dataclass
class FactCheckResult:
    """Результат проверки фактов"""
    has_conflicts: bool  # Есть ли противоречия
    inconsistencies: List[Dict[str, str]]  # Список найденных противоречий
    confidence: float  # Уверенность в результате (0-1)
    relevant_facts: List[str]  # Использованные для проверки факты
    explanation: str  # Объяснение результата

class FactConsistencyChecker:
    """
    Основной класс для проверки фактологической согласованности текстов.
    Координирует работу компонентов RAG-системы: разбиение текста, 
    векторный поиск и взаимодействие с LLM.
    """
    
    def __init__(
        self,
        llm_service: Any,  # Сервис для работы с LLM
        config: List[Union[float, int]] = [0.1, 1000]
    ):
        """
        Инициализация системы проверки фактов.
        
        Args:
            llm_service: Сервис для работы с LLM
            config: Конфигурация системы
        """
        self.llm_service = llm_service
        self.config = config
        
        self.logger = logging.getLogger(__name__)
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Настройка логирования"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )



    def check_facts(self, text: str, relevant_facts: List[str]) -> FactCheckResult:
        """
        Проверка фактологической согласованности текста.
        
        Args:
            text: Текст для проверки
        
        Returns:
            Результат проверки фактов
        """
        self.logger.info("Начало проверки фактов")
        try:            
            # Формирование промпта для LLM
            prompt = self._create_prompt(text, relevant_facts)

            # Формирование системного промпта
            system_prompt = self._get_system_prompt()

            
            # Получение и обработка ответа от LLM
            llm_response = self.llm_service.analyze_consistency(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=self.config[0],
                max_tokens=self.config[1]
            )

            # Парсим ответ LLM в JSON

            try:
                parsed_result = json.loads(llm_response)
                self._validate_response(parsed_result)
                
            except json.JSONDecodeError as e:
                print(llm_response)
                raise ValueError(f"Ошибка парсинга JSON ответа: {str(e)}")

            
            # Парсим JSON в структуру FactCheckResult
            result = self._parse_llm_response(parsed_result, relevant_facts)
            
            self.logger.info(
                f"Проверка завершена. "
                f"Найдено противоречий: {len(result.inconsistencies)}"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Ошибка при проверке фактов: {str(e)}")
            raise



    def _validate_response(self, response: Dict[str, Any]) -> None:
        """
        Проверка структуры ответа от модели.
        
        Args:
            response: Ответ от модели
        
        Raises:
            ValueError: Если структура ответа некорректна
        """
        required_fields = ['has_conflicts', 'inconsistencies', 'confidence', 'explanation']
        
        # Проверяем наличие всех необходимых полей
        if not all(field in response for field in required_fields):
            raise ValueError("В ответе отсутствуют обязательные поля")
        
        # Проверяем типы данных
        if not isinstance(response['has_conflicts'], bool):
            raise ValueError("Поле 'has_conflicts' должно быть boolean")
        
        if not isinstance(response['inconsistencies'], list):
            raise ValueError("Поле 'inconsistencies' должно быть списком")
        
        if not isinstance(response['confidence'], (int, float)):
            raise ValueError("Поле 'confidence' должно быть числом")
        
        if not isinstance(response['explanation'], str):
            raise ValueError("Поле 'explanation' должно быть строкой")
        
        # Проверяем структуру inconsistencies
        for inc in response['inconsistencies']:
            if not all(k in inc for k in ['statement', 'fact', 'explanation']):
                raise ValueError("Некорректная структура элемента inconsistencies")



    def _create_prompt(self, text: str, facts: List[str]) -> str:
        """
        Формирование промпта для LLM.
        
        Args:
            text: Проверяемый текст
            facts: Релевантные факты из базы знаний
        
        Returns:
            Промпт для LLM
        """
        formatted_facts = "\n".join(f"- {fact}" for fact in facts)
        prompt_template = f"""Входной текст для проверки: {text}
        Известные факты: {formatted_facts}"""
        
        return prompt_template

    def _get_system_prompt(self) -> str:
        """
        Получение системного промпта для модели.
        
        Returns:
            Системный промпт
        """
        with open("system_prompt.txt", "r") as f:
            return f.read()

    def _parse_llm_response(
        self,
        response: Dict[str, Any],
        relevant_facts: List[str]
    ) -> FactCheckResult:
        """
        Преобразование ответа LLM в структурированный результат.
        
        Args:
            response: Ответ от LLM
            relevant_facts: Использованные факты
        
        Returns:
            Структурированный результат проверки
        """
        return FactCheckResult(
            has_conflicts=response["has_conflicts"],
            inconsistencies=response["inconsistencies"],
            confidence=response["confidence"],
            relevant_facts=relevant_facts,
            explanation=response["explanation"]
        ) 