#!/usr/bin/env python3
"""
Скрипт для запуска frontend сервера
"""

import os
import sys
import subprocess
import time

def check_neo4j():
    """Проверка доступности Neo4j"""
    try:
        import neo4j
        driver = neo4j.GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "enrico-cecilia-cable-uranium-twin-190"))
        with driver.session() as session:
            session.run("RETURN 1")
        print("✅ Neo4j подключен успешно")
        return True
    except Exception as e:
        print(f"❌ Ошибка подключения к Neo4j: {e}")
        print("Убедитесь, что Neo4j запущен на bolt://localhost:7687")
        return False

def install_requirements():
    """Установка зависимостей"""
    print("Установка зависимостей...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Зависимости установлены")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка установки зависимостей: {e}")
        return False

def main():
    print("🚀 Запуск frontend для поиска в документации")
    print("=" * 50)
    
    # Проверяем зависимости
    if not install_requirements():
        return
    
    # Проверяем Neo4j
    if not check_neo4j():
        print("\n⚠️  Внимание: Neo4j недоступен, но сервер все равно запустится")
        print("   Граф будет инициализирован при первом запросе")
    
    print("\n🌐 Запуск веб-сервера...")
    print("Откройте http://localhost:5000 в браузере")
    print("Для остановки нажмите Ctrl+C")
    print("=" * 50)
    
    # Запускаем Flask сервер
    try:
        from app import app
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n👋 Сервер остановлен")
    except Exception as e:
        print(f"❌ Ошибка запуска сервера: {e}")

if __name__ == "__main__":
    main()



