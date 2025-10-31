from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os


app = Flask(__name__)
CORS(app, origins="https://barbalao.vercel.app/") 

# função para abrir e fechar a conexão com o banco, ao inves de ficar aberto toda hora tava dando DB is locked
def get_conn():
    caminhoBanco = os.path.join(os.path.dirname(__file__), '..', 'db', 'barbalao.db')
    conn = sqlite3.connect(caminhoBanco)
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/api/login', methods=['POST'])
def api_server():
        try:
            
            data = request.get_json()

            if data == None:
                return jsonify({
                "route": "/login",
                "message": "JSON inválido ou ausente na requisição"
            }), 400

            nome = data.get('nome')
            senha = data.get('senha')

            conn = get_conn()
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM users WHERE nome = ?', (nome,))
            usuario = cursor.fetchone()

            conn.close()
        
            if usuario != None:
                if usuario[2] == senha:
                        result = {
                            "route": "/form", 
                            "message": "OK"
                        }
                        print(result)
                        return jsonify(result), 200
                
                return jsonify({
                "route": "/login",
                "message": "Usuário ou senha incorretos"
            }), 400

        except TypeError as e:
             print(f"Erro usuário não encontrado: {e}")        
        return jsonify({"route": "/login", "status": 500})

if __name__ == '__main__':
    app.run(port=3001)