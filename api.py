from flask import Flask, request, jsonify
import os
from encrypt import verify_password
from apiProd import app, get_conn

@app.route('/api/login/', methods=['POST'])
def api_server():
        if request.method == 'OPTIONS':
            return jsonify({"message": "CORS preflight OK"}), 200
        data = request.get_json()
        try:

            if data == None:
                return jsonify({
                "message": "JSON inválido ou ausente na requisição"
            }), 400

            nome = data.get('nome')
            senha = data.get('senha')

            conn = get_conn()
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM users WHERE nome = ?', (nome,))
            usuario = cursor.fetchone()
            
            if usuario != None:
                if verify_password(usuario[2], senha):
                        result = {
                            "message": "OK"
                        }
                        print(result)
                        return jsonify(result), 200
                
                return jsonify({
                "message": "Usuário ou senha incorretos"
            }), 400

            conn.close()
        except TypeError as e:
             print(f"Erro usuário não encontrado: {e}")        
        return jsonify({"route": "/login", "status": 500})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Render define PORT
    app.run(host="0.0.0.0", port=port)
