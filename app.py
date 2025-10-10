from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import subprocess
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# Конфигурация
UPLOAD_FOLDER = 'input_data'
ALLOWED_EXTENSIONS = {'txt'}
INPUT_JSON_PATH = 'input.json'

# Создаем папку для загрузки файлов, если её нет
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'Файл не найден в запросе'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'Файл не выбран'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        return jsonify({
            'success': True,
            'message': 'Файл успешно загружен',
            'file_path': file_path
        })
    
    return jsonify({'success': False, 'message': 'Недопустимый тип файла'}), 400

@app.route('/api/query', methods=['POST'])
def query():
    data = request.json
    if not data or 'input_data' not in data:
        return jsonify({'success': False, 'message': 'Отсутствуют данные запроса'}), 400

    # Формируем input.json с фиксированными полями
    input_json_data = {
        'conflict': data['input_data'].get('conflict', ''),
        'format': 'text',
        'data_path': 'input_data',
        'chunker': 'basic'
    }

    # Сохраняем input.json
    with open(INPUT_JSON_PATH, 'w') as f:
        json.dump(input_json_data, f)

    try:
        # Запускаем main.py с нужными параметрами
        cmd = ['python3', 'main.py', '--input_json', INPUT_JSON_PATH]
        if data.get('has_graph'):
            cmd.extend(['--has_graph', 'true'])
        
        # Запускаем процесс и получаем вывод
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print("Error output:", result.stderr)
            return jsonify({
                'success': False,
                'message': 'Ошибка при обработке запроса',
                'details': result.stderr
            }), 500

        # Парсим результат из stdout
        try:
            response_data = json.loads(result.stdout)
            return jsonify(response_data)
        except json.JSONDecodeError:
            print("Raw output:", result.stdout)
            return jsonify({
                'success': False,
                'message': 'Ошибка при парсинге результата'
            }), 500

    except Exception as e:
        print("Exception:", str(e))
        return jsonify({
            'success': False,
            'message': 'Внутренняя ошибка сервера',
            'details': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 