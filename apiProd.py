from flask import Flask, request, jsonify, session, render_template_string
from encrypt import verify_password, hash_password
from datetime import timedelta
from flask_cors import CORS
import psycopg2
import os
import traceback

app = Flask(__name__)

# ================== CORS ======================
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:5173",
            "https://barbalao.vercel.app",
            "https://supreme-carnival-x5xvwq7494qxh6r7j-5173.app.github.dev",
            "https://dark-sorcery-q76pqgjx9r6q2xqrj-5173.app.github.dev",
            "https://dark-sorcery-q76pqgjx9r6q2xqrj-5174.app.github.dev"
        ],
        "supports_credentials": True,
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# ================== CONFIGURAÇÕES ======================
app.secret_key = '4af61d297ff9bcb7358f01f9ae61a6fc'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
cookie_value = "wekdoWKGFKGK1234553"

# ⚙️ Configuração dinâmica: local vs produção
if os.environ.get("RENDER") == "true":
    app.config.update(
        SESSION_COOKIE_SAMESITE='None',
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_DOMAIN=".onrender.com"
    )
else:
    app.config.update(
        SESSION_COOKIE_SAMESITE='Lax',
        SESSION_COOKIE_SECURE=False,
        SESSION_COOKIE_DOMAIN=None
    )

# ================== BANCO DE DADOS ======================
def get_conn():
    conn = psycopg2.connect(
        dbname="banco_barbalao",
        user="root",
        password="DdDLJr8BYykOf9hJL9TWXP2eDsF2A8S6",
        host="dpg-d42kp3i4d50c739qr750-a.oregon-postgres.render.com",
        port="5432"
    )
    return conn

# ================== ROTAS ======================
@app.route('/', methods=['GET'])
def init():
    return render_template_string("<h1>API Barbalao funcionando ✅</h1>")

# ========== LOGIN ==========
@app.route('/api/login/', methods=['POST'])
def api_login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "JSON inválido ou ausente"}), 400

        nome = data.get('nome_user')
        senha = data.get('senha')  # <-- alterado: senha em texto, não hash

        if not nome or not senha:
            return jsonify({"message": "Campos 'nome_user' e 'senha' são obrigatórios"}), 400

        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM usuario WHERE nome_user = %s', (nome,))
        usuario = cursor.fetchone()

        if not usuario:
            return jsonify({"message": "Usuário não encontrado"}), 404

        # ⚠️ Ajuste o índice conforme a posição da senha no banco
        senha_hash_banco = usuario[2]

        if verify_password(senha, senha_hash_banco):
            session["usuario"] = usuario[1]
            session["token"] = cookie_value
            session.permanent = True

            print("✅ Sessão criada com sucesso:", dict(session))
            return jsonify({"message": "OK"}), 200
        else:
            return jsonify({"message": "Usuário ou senha incorretos"}), 401

    except Exception as e:
        print("🚨 Erro interno no login:", str(e))
        traceback.print_exc()
        return jsonify({"message": f"Erro no servidor: {str(e)}"}), 500

    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass

# ========== CHECA SESSÃO ==========
@app.route('/api/check_session/', methods=['GET'])
def check_session():
    print("Sessão atual:", dict(session))
    if "usuario" in session:
        return jsonify({
            "authenticated": True,
            "usuario": session["usuario"]
        }), 200
    else:
        return jsonify({"authenticated": False}), 401

# ========== CRIAR PRODUTO ==========
@app.route('/api/products/', methods=['POST'])
def create_product():
    try:
        data = request.get_json()
        if data is None:
            return jsonify({"message": "JSON inválido ou ausente"}), 400
        
        nome = data.get('nome_prod')
        preco = data.get('preco_prod')
        descricao = data.get('descricao_prod')
        imagem = data.get('imagem_prod')

        if not nome or preco is None:
            return jsonify({"message": "Campos obrigatórios: nome_prod e preco_prod"}), 400

        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO produto(nome_prod, preco_prod, descricao_prod, imagem_prod)
            VALUES (%s, %s, %s, %s)
            RETURNING id_prod
            ''', (nome, float(preco), descricao, imagem)
        )

        new_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Produto Criado", "ID": new_id}), 201

    except Exception as e:
        print(f"Erro ao criar produto: {e}")
        traceback.print_exc()
        return jsonify({"message": f"Erro interno: {str(e)}"}), 500

# ========== LISTAR PRODUTOS ==========
@app.route('/api/products/', methods=['GET'])
def list_products():
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT id_prod, nome_prod, preco_prod, descricao_prod, imagem_prod FROM produto;')
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        products = [
            {
                'id_prod': row[0],
                'nome_prod': row[1],
                'preco_prod': float(row[2]),
                'descricao_prod': row[3],
                'imagem_prod': row[4]
            } for row in rows
        ]
        return jsonify(products), 200

    except Exception as e:
        print(f"Erro ao listar produtos: {e}")
        traceback.print_exc()
        return jsonify({"message": "Erro Interno"}), 500

# ========== ATUALIZAR PRODUTO ==========
@app.route('/api/products/atualizar/<int:product_id>/', methods=['POST'])
def update_products(product_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "JSON inválido ou ausente"}), 400

        nome = data.get('nome_prod')
        preco = data.get('preco_prod')
        imagem = data.get('imagem_prod')

        conn = get_conn()
        cursor = conn.cursor()

        if nome:
            cursor.execute('UPDATE produto SET nome_prod = %s WHERE id_prod = %s;', (nome, product_id))
        if preco:
            cursor.execute('UPDATE produto SET preco_prod = %s WHERE id_prod = %s;', (preco, product_id))
        if imagem:
            cursor.execute('UPDATE produto SET imagem_prod = %s WHERE id_prod = %s;', (imagem, product_id))

        conn.commit()
        updated = cursor.rowcount
        cursor.close()
        conn.close()

        if updated == 0:
            return jsonify({"message": "Produto não encontrado"}), 404
        
        return jsonify({"message": "Produto atualizado com sucesso"}), 200

    except Exception as e:
        print(f"Erro ao atualizar produto: {e}")
        traceback.print_exc()
        return jsonify({"message": f"Erro Interno: {str(e)}"}), 500

# ========== REMOVER PRODUTO ==========
@app.route('/api/products/remove/<int:product_id>/', methods=['DELETE'])
def remove_product(product_id):
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM produto WHERE id_prod = %s', (product_id,))
        conn.commit()
        deleted = cursor.rowcount
        cursor.close()
        conn.close()

        if deleted == 0:
            return jsonify({"message": "Produto não encontrado"}), 404

        return jsonify({"message": "Produto removido com sucesso"}), 200

    except Exception as e:
        print(f"Erro ao remover produto: {e}")
        traceback.print_exc()
        return jsonify({"message": f"Erro interno: {str(e)}"}), 500

# ================== MAIN ======================
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
