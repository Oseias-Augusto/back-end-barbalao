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

            cursor.execute('SELECT * FROM users WHERE nome = %s', (nome,))
            usuario = cursor.fetchone()
            if usuario:
                if verify_password(usuario[1], senha):
                    return jsonify({"message": "OK"}), 200
                else:
                    return jsonify({"message": "Usuário ou senha incorretos"}), 401
            else:
                return jsonify({"message": "Usuário não encontrado"}), 404

        except TypeError as e:
             print(f"Erro usuário não encontrado: {e}")
             cursor.close()
             conn.close()    
        return jsonify({"route": "/login", "status": 500})

