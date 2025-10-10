#!/usr/bin/env python3
"""
Простой HTTP сервер для frontend без Flask
Использует встроенный http.server для статических файлов
"""

import http.server
import socketserver
import json
import os
import sys
import urllib.parse
from pathlib import Path

# Добавляем путь к основному проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Кастомный обработчик HTTP запросов"""
    
    def do_GET(self):
        """Обработка GET запросов"""
        if self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'status': 'ok',
                'message': 'Простой сервер работает',
                'note': 'Для полной функциональности нужен Flask сервер'
            }
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            return
        
        # Для всех остальных запросов используем стандартную обработку
        super().do_GET()
    
    def do_POST(self):
        """Обработка POST запросов"""
        if self.path == '/api/search':
            self.send_response(501)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'error': 'Функция поиска недоступна',
                'message': 'Для поиска в документах нужен Flask сервер с подключением к backend',
                'suggestion': 'Запустите app.py для полной функциональности'
            }
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            return
        
        # Для остальных POST запросов
        self.send_response(404)
        self.end_headers()
    
    def end_headers(self):
        """Добавляем CORS заголовки"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def main():
    """Запуск простого HTTP сервера"""
    PORT = 8000
    
    # Переходим в директорию frontend_new
    frontend_dir = Path(__file__).parent
    os.chdir(frontend_dir)
    
    print("🚀 Запуск простого HTTP сервера для frontend")
    print("=" * 50)
    print(f"📁 Директория: {frontend_dir}")
    print(f"🌐 URL: http://localhost:{PORT}")
    print("📝 Примечание: Это демо-версия без backend функциональности")
    print("   Для полной функциональности запустите: python3 app.py")
    print("=" * 50)
    
    try:
        with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
            print(f"✅ Сервер запущен на порту {PORT}")
            print("   Откройте http://localhost:8000 в браузере")
            print("   Для остановки нажмите Ctrl+C")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Сервер остановлен")
    except Exception as e:
        print(f"❌ Ошибка запуска сервера: {e}")

if __name__ == "__main__":
    main()



