import os
import psycopg2
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    if not DATABASE_URL:
        return None 
    conn = psycopg2.connect(DATABASE_URL)
    return conn

def init_db():
    """Создаёт таблицу, если БД доступна"""
    if not DATABASE_URL:
        print("⚠️ DATABASE_URL не задана, пропускаем инициализацию БД")
        return
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            )
        ''')
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Таблица создана/проверена")
    except Exception as e:
        print(f"⚠️ Ошибка подключения к БД: {e}")

if DATABASE_URL:
    init_db()
else:
    print("⚠️ DATABASE_URL не задана, БД не инициализирована")

@app.route('/api/data', methods=['GET'])
def get_items():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, name, created_at FROM items ORDER BY id DESC')
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    items = [{'id': row[0], 'name': row[1], 'created_at': row[2]} for row in rows]
    return jsonify(items)

@app.route('/api/data', methods=['POST'])
def add_item():
    data = request.get_json()
    name = data.get('name')
    if not name:
        return jsonify({'error': 'Name is required'}), 400
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO items (name) VALUES (%s) RETURNING id', (name,))
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify({'id': new_id, 'name': name}), 201

@app.route('/api/data/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM items WHERE id = %s', (item_id,))
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify({'message': 'Deleted'}), 200

@app.route('/')
def root():
    return {
        'message': 'API is running',
        'endpoints': {
            'GET /api/data': 'Get all items',
            'POST /api/data': 'Add new item',
            'DELETE /api/data/<id>': 'Delete item'
        }
    }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)