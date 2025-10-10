import pandas as pd
from typing import List, Tuple
from fact_checker import FactConsistencyChecker
from llm_service import YandexCloudLLM
from tokens import *

def load_test_data(csv_path: str, max_rows: int = 20) -> pd.DataFrame:
    """
    Загрузка тестовых данных из CSV файла.
    
    Args:
        csv_path: Путь к CSV файлу
        max_rows: Максимальное количество строк для обработки
    
    Returns:
        DataFrame с тестовыми данными
    """
    df = pd.read_csv(csv_path)
    return df.head(max_rows)  # Берем только первые max_rows строк

def evaluate_checker(
    checker: FactConsistencyChecker,
    test_data: pd.DataFrame
) -> Tuple[float, List[dict]]:
    """
    Оценка точности работы чекера на тестовых данных.
    
    Args:
        checker: Инициализированный чекер
        test_data: DataFrame с тестовыми данными
    
    Returns:
        Точность (процент совпадений) и список результатов
    """
    total_cases = len(test_data)
    correct_predictions = 0
    detailed_results = []
    
    for idx, row in test_data.iterrows():
        try:
            # Получаем результат от чекера
            result = checker.check_facts(
                text=row['query'],  # Используем 'query' вместо 'text_to_check'
                relevant_facts=[row['contradiction']]  # Используем 'contradiction' вместо 'facts'
            )
            
            # Преобразуем строковое значение 'result' в булево
            expected_result = row['result']
            
            # Сравниваем с ожидаемым результатом
            is_correct = result.has_conflicts == expected_result
            
            if is_correct:
                correct_predictions += 1
            
            # Сохраняем детали для анализа
            detailed_results.append({
                'query': row['query'],
                'contradiction': row['contradiction'],
                'expected': expected_result,
                'predicted': result.has_conflicts,
                'is_correct': is_correct,
                'confidence': result.confidence,
                'explanation': result.explanation
            })
            
            # Выводим прогресс
            print(f"Обработано {idx + 1}/{total_cases} случаев...")
            
        except Exception as e:
            print(f"Ошибка при обработке строки {idx}: {str(e)}")
            detailed_results.append({
                'query': row['query'],
                'contradiction': row['contradiction'],
                'expected': row['result'],
                'predicted': None,
                'is_correct': False,
                'confidence': None,
                'explanation': f"Ошибка: {str(e)}"
            })
    
    accuracy = (correct_predictions / total_cases) * 100
    # Вычисляем метрики precision и recall
    true_positives = sum(1 for r in detailed_results if r['predicted'] == True and r['expected'] == True)
    false_positives = sum(1 for r in detailed_results if r['predicted'] == True and r['expected'] == False)
    false_negatives = sum(1 for r in detailed_results if r['predicted'] == False and r['expected'] == True)
    
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    
    print(f"Accuracy: {accuracy:.2f}%")
    print(f"Precision: {precision:.2f}")
    print(f"Recall: {recall:.2f}")
    return accuracy, detailed_results

def save_results(
    accuracy: float,
    detailed_results: List[dict],
    output_path: str = "evaluation_results.csv"
):
    """
    Сохранение результатов оценки в CSV файл.
    
    Args:
        accuracy: Процент совпадений
        detailed_results: Список с детальными результатами
        output_path: Путь для сохранения результатов
    """
    # Сохраняем детальные результаты
    results_df = pd.DataFrame(detailed_results)
    results_df.to_csv(output_path, index=False)
    
    # Сохраняем общую статистику
    with open("evaluation_summary.txt", "w") as f:
        f.write(f"Общая точность: {accuracy:.2f}%\n")
        f.write(f"Всего случаев: {len(detailed_results)}\n")
        f.write(f"Правильных предсказаний: {sum(r['is_correct'] for r in detailed_results)}\n")
        
        # Добавляем статистику по уверенности модели
        confidences = [r['confidence'] for r in detailed_results if r['confidence'] is not None]
        if confidences:
            avg_confidence = sum(confidences) / len(confidences)
            f.write(f"Средняя уверенность модели: {avg_confidence:.2f}\n")

def main():
    # Инициализация сервисов
    api_key = AUTH_TOKEN
    folder_id = FOLDER_ID

    
    llm_service = YandexCloudLLM(
        api_key=api_key,
        folder_id=folder_id,
        model_uri="yandexgpt-lite", #"llama-lite"
        temperature=0.1
    )
    
    checker = FactConsistencyChecker(llm_service=llm_service)
    
    try:
        # Загрузка тестовых данных (только первые 20 строк)
        test_data = load_test_data("contradict_query.csv", max_rows=100)
        print((test_data['result'] == True).sum())
        
        print(f"Загружено {len(test_data)} тестовых случаев")
        
        # Оценка чекера
        accuracy, detailed_results = evaluate_checker(checker, test_data)
        
        # Сохранение результатов
        save_results(accuracy, detailed_results)
        
        # Вывод результатов
        print(f"\nОценка завершена!")
        print(f"Общая точность: {accuracy:.2f}%")
        print(f"Подробные результаты сохранены в evaluation_results.csv")
        print(f"Сводная статистика сохранена в evaluation_summary.txt")
        
    except Exception as e:
        print(f"Произошла ошибка при выполнении оценки: {str(e)}")

if __name__ == "__main__":
    main() 