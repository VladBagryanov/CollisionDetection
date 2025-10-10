import os
from typing import List
from fact_checker import FactCheckResult, FactConsistencyChecker
from llm_service import YandexCloudLLM
from tokens import *

def format_result(result: FactCheckResult) -> str:
    """
    Форматирование результата проверки в читаемый текст.
    
    Args:
        result: Результат проверки фактов
    
    Returns:
        Отформатированный текст с результатами
    """
    output = []
    
    # Основной вывод
    output.append("=== Результат проверки фактов ===\n")
    output.append(f"Текст {'согласован' if result.has_conflicts else 'не согласован'} с фактами")
    output.append(f"Уверенность: {result.confidence:.2f}\n")
    
    # Найденные противоречия
    if result.inconsistencies:
        output.append("Найденные противоречия:")
        for i, inc in enumerate(result.inconsistencies, 1):
            output.append(f"\n{i}. Противоречие:")
            output.append(f"   Утверждение: {inc['statement']}")
            output.append(f"   Противоречит факту: {inc['fact']}")
            output.append(f"   Объяснение: {inc['explanation']}")
    else:
        output.append("Противоречий не найдено.")

    # Подтверждающие факты
    if result.supporting_facts:
        output.append("\nПодтверждающие факты:")
        for i, sup in enumerate(result.supporting_facts, 1):
            output.append(f"\n{i}. Подтверждение:")
            output.append(f"   Утверждение: {sup['statement']}")
            output.append(f"   Подтверждается фактом: {sup['fact']}")
            output.append(f"   Объяснение: {sup['explanation']}")
    else:
        output.append("\nПодтверждающих фактов не найдено.")
    
    # Использованные факты
    output.append("\nИспользованные факты для проверки:")
    for i, fact in enumerate(result.relevant_facts, 1):
        output.append(f"{i}. {fact}")
    
    # Общее объяснение
    output.append(f"\nПодробное объяснение:\n{result.explanation}")
    
    return "\n".join(output)


def main():
    # API ключи
    api_key = AUTH_TOKEN
    folder_id = FOLDER_ID
    
    if not api_key or not folder_id:
        print("Ошибка: Не установлены API ключи")
        return
    
    # Тестовые данные
    # Пример 2: Утверждение не противоречит фактам
    text_to_check = """
        Юпитер — самая большая планета Солнечной системы, у него нет твердой поверхности.
    """

    facts = [
        "Юпитер — крупнейшая планета в Солнечной системе.",
        "Юпитер является газовым гигантом и не имеет твердой поверхности."
    ]
    
    try:
        # Проверка текста
        llm_service = YandexCloudLLM(
            api_key=api_key,
            folder_id=folder_id,
            model_uri="yandexgpt-lite", #"llama-lite"
            temperature=0.1
        )
        a = FactConsistencyChecker(llm_service=llm_service)
        result = a.check_facts(text_to_check, facts)
        
        # Вывод результата
        print(format_result(result))
        
        
        
    except Exception as e:
        print(f"Произошла ошибка при проверке текста: {str(e)}")

if __name__ == "__main__":
    main() 