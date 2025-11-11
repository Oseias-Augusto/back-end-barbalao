from flask import Flask, request, jsonify, session
from encrypt import verify_password, hash_password
from datetime import timedelta
from flask_cors import CORS
import psycopg2
import os

app = Flask(__name__)
app.secret_key = '4af61d297ff9bcb7358f01f9ae61a6fc'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)

# Configuração CORRETA do CORS
CORS(app, 
     origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "https://barbalao.vercel.app",
        "https://supreme-carnival-x5xvwq7494qxh6r7j-5173.app.github.dev",
        "https://dark-sorcery-q76pqgjx9r6q2xqrj-5173.app.github.dev",
        "https://dark-sorcery-q76pqgjx9r6q2xqrj-5174.app.github.dev"
     ],
     supports_credentials=True,  # 🔑 IMPORTANTE
     allow_headers=["Content-Type", "Authorization"]
)

# Configuração CORRETA da sessão
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=True,  # Mude para True em produção
    SESSION_COOKIE_SAMESITE='None',  # Para cross-site
)

def get_conn():
    conn = psycopg2.connect(
        dbname="banco_barbalao",  
        user="root",       
        password="DdDLJr8BYykOf9hJL9TWXP2eDsF2A8S6",    
        host="dpg-d42kp3i4d50c739qr750-a.oregon-postgres.render.com",            
        port="5432"      
    )
    return conn

@app.route('/api/login/', methods=['POST', 'OPTIONS'])
def api_server():
    if request.method == 'OPTIONS':
        return jsonify({"message": "CORS preflight OK"}), 200
    
    data = request.get_json()
    try:
        if data is None:
            return jsonify({
                "message": "JSON inválido ou ausente na requisição"
            }), 400

        nome = data.get('nome')
        senha = data.get('senha')

        conn = get_conn()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM usuario WHERE nome_user = %s', (nome,))
        usuario = cursor.fetchone()

        if usuario and verify_password(usuario[2], senha):
            # 🔑 CORREÇÃO: Configuração correta da sessão
            session['user'] = usuario[1]
            session.permanent = True
            
            response = jsonify({"message": "OK", "user": usuario[1]})
            
            conn.close()
            cursor.close()
            return response, 200
        else:
            cursor.close()
            conn.close()
            return jsonify({"message": "Usuário ou senha incorretos"}), 401

    except Exception as e:
        print(f"Erro no login: {e}")
        return jsonify({"message": "Erro no servidor, tente mais tarde"}), 500

@app.route('/api/check_session/', methods=['GET'])
def check_session():
    if 'user' in session:
        return jsonify({
            "authenticated": True, "user": session['user']
        }), 200
    else:
        return jsonify({"authenticated": False}), 401

# CREATE ('C'RUD) -------------------------------------------------------------------------------------------------------------------

#PROD ---------------------------------------
@app.route('/api/products/', methods=['POST'])
def create_product():
    try:
        data = request.get_json()
        print("Dados recebidos:", data)

        if data is None:
            print("JSON ausente ou inválido")
            return jsonify({"message": "JSON inválido ou ausente"}), 400
        
        nome = data.get('nome')
        preco = data.get('preco')
        descricao = data.get('descricao')
        imagem = data.get('imagem')
        categoria = data.get('categoria')
        usuario = data.get('usuario')

        print(f"Nome: {nome}, Preço: {preco}, Imagem: {type(imagem)}")

        if not nome or preco is None:
            print("Campos obrigatórios ausentes")
            return jsonify({"message": "Campos obrigatórios: name e preco_prod"}), 400

        conn = get_conn()
        cursor = conn.cursor()

        cursor.execute(
            '''
             INSERT INTO produto(nome_prod, preco_prod, descricao_prod, imagem_prod, categoria_id_categoria, usuario_id_user)
             VALUES (%s, %s, %s, %s, %s, %s)
             RETURNING id_prod
            ''', (nome, float(preco), descricao, imagem, categoria, usuario)
        )
        
        conn.commit()
        new_id = cursor.fetchone()[0]
        print("Produto criado com ID:", new_id)

        conn.close()
        
        return jsonify({"message": "Produto Criado", "ID" : new_id}), 201

    except Exception as e:
        print(f"Erro ao criar produto: {e}")
        return jsonify({"message": f"Erro interno: {str(e)}"}), 500
    

#CATEG -------------------------------------------------------
@app.route('/api/categoria/', methods = ['POST'])
def create_categ():
    try:
        data = request.get_json()
        print(f"Dados recebidos: {data}")

        if data is None:
            print("JSON ausente ou inválido")
            return jsonify({"message": "JSON inválido ou ausente"}), 400
        
        nome = data.get('nome')
        imagem = data.get('imagem')
        usuario = data.get('usuario')
        categoria = data.get('sub')

        print(f"Nome: {nome}, Imagem: {imagem}, usuario: {usuario}, categoria: {categoria}")

        if nome is None or imagem is None:
            print("Campos obrigatórios ausentes")
            return jsonify({"message": "Campos obrigatórios: nome e imagem"}), 400

        conn = get_conn()
        cursor = conn.cursor()

        if categoria is None:
            cursor.execute(
                '''
                    INSERT INTO categoria (nome_categ, imagm_categ, usuario_id_user)
                    VALUES(%s, %s, %s)
                ''',(nome, imagem, usuario)
            )
        else:
            cursor.execute(
                '''
                    INSERT INTO categoria (nome_categ, imagm_categ, usuario_id_user, categoria_id_categoria)
                    VALUES(%s, %s, %s, %s)
                ''',(nome, imagem, usuario, categoria)
            )

        conn.commit()
        new_id = cursor.fetchone()[0]
        print("Categoria criada com ID:", new_id)

        conn.close()
        
        return jsonify({"message": "Categoria Criada", "ID" : new_id}), 201

    
    except Exception as e:
        print(f"Erro ao criar categoria: {e}")
        return jsonify({"message": f"Erro interno: {str(e)}"}), 500

#BANNER ------------------------------------------------------
@app.route('api/banner/', methods = ['POST'])
def create_banner():
    try:
        data = request.get_json()
        print(f"Dados recebidos: {data}")

        if data is None:
            print("JSON ausente ou inválido")
            return jsonify({"message": "JSON inválido ou ausente"}), 400
    
        titulo = data.get('titulo')
        sub_titulo = data.get('sub_titulo')
        imagem = data.get('imagem')
        usuario = data.get('usuario')

        print(f"titulo: {titulo}, sub_titulo: {sub_titulo}, imagem: {imagem}, usuario: {usuario}")

        if titulo is None or imagem is None:
            print('Campos obrigatorios ausentes')
            return jsonify({"message": "Campos obrigatorios: titulo e imagem"}), 400
        
        conn = get_conn()
        cursor = conn.cursor()

        cursor.execute(
            '''
                INSERT INTO banners (titulo_banner, sub_titulo_banner, imagem_banner, usuario_id_user)
                VALUES(%s, %s, %s, %s)
            ''', (titulo, sub_titulo, imagem, usuario)
        )

        conn.commit()

        new_id = cursor.fetchone()[0]
        print("Banner criado com ID:", new_id)

        conn.close()
        
        return jsonify({"message": "Banner Criada", "ID" : new_id}), 201

    except Exception as e:
        print(f"Erro ao criar categoria: {e}")
        return jsonify({"message": f"Erro interno: {str(e)}"}), 500



# REED (C'R'UD) --------------------------------------------------------------------------------------------------------------------

#PRODUTO -----------------------------------
@app.route('/api/products/', methods=['GET'])
def list_products():
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id_prod, nome_prod, preco_prod, 
                   descricao_prod, imagem_prod 
            FROM produto;''')
        rows = cursor.fetchall()

        conn.close()

        products = [
            {
                'id_prod': row[0],
                'nome': row[1],
                'preco': float(row[2]),
                'descricao': row[3],
                'imagem': row[4]
            } for row in rows
        ]

        return jsonify(products), 200
    
    except Exception as e:
        print(f"Erro ao criar produto: {e}")
        return jsonify({"message": "Erro Interno"}), 500
    
#CATEGORIA ----------------------------------------------

# Pega subcategorias
@app.route('/api/categoria/', methods = ['GET'])
def list_categ():
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT sub.id_categoria, sub.nome_categ, sub.usuario_id_user, 
                   sub.categoria_id_categoria,
                   categ.nome_categ as nome_categoria_pai
            FROM categoria sub 
            LEFT JOIN categoria categ ON sub.categoria_id_categoria = categ.id_categoria;
        ''')
        rows = cursor.fetchall()

        conn.close()

        categories = [
            {
                'id_categoria': row[0],
                'nome': row[1],
                'usuario': row[2],
                'sub_categoria_de': row[3],
                'nome_categoria_pai': row[4]
            } for row in rows
        ]

        return jsonify(categories), 200
    
    except Exception as e:
        print(f"Erro ao listar categorias: {e}")
        return jsonify({"message": "Erro Interno"}), 500

# So as cetegorias pai
@app.route('/api/categoria/principais/', methods = ['GET'])
def list_categ_principais():
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id_categoria, nome_categ, imagm_categ, usuario_id_user
            FROM categoria 
            WHERE categoria_id_categoria IS NULL;
        ''')
        rows = cursor.fetchall()

        conn.close()

        categories = [
            {
                'id_categoria': row[0],
                'nome': row[1],
                'imagem': row[2],
                'usuario': row[3]
            } for row in rows
        ]

        return jsonify(categories), 200
    
    except Exception as e:
        print(f"Erro ao listar categorias principais: {e}")
        return jsonify({"message": "Erro Interno"}), 500

#BANNER ---------------------------------------------------
@app.route('/api/banner/', method=['GET'])
def list_banner():
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id_banner, titulo_banner, 
                   sub_titulo_banner, imagem_banner, 
                   usuario_id_user 
            FROM banners;''')
        rows = cursor.fetchall()

        conn.close()

        categories = [
            {
                'id_banner': row[0],
                'titulo': row[1],
                'sub_titulo': row[2],
                'imagem': row[3],
                'usuario': row[4]
            } for row in rows
        ]

        return jsonify(categories), 200
    
    except Exception as e:
        print(f"Erro ao criar categoria: {e}")
        return jsonify({"message": "Erro Interno"}), 500


# Atualizar Prod.
@app.route('/api/products/atualizar/<int:product_id>/', methods=['POST'])
def update_products(product_id, product_name = None, product_image = None, product_price = None):
    try:
        conn = get_conn()
        cursor = conn.cursor()
        if product_name:
            cursor.execute('UPDATE produto SET nome_prod = %s WHERE id_prod = %s;', (product_name, product_id))
        if product_image:
            cursor.execute('UPDATE produto SET imagem_prod = %s WHERE id_prod = %s;', (product_image, product_id))
        if product_price:
            cursor.execute('UPDATE produto SET preco_prod = %s WHERE id_prod = %s;', (product_image, product_id))

        conn.commit()
        cursor.close()

        if cursor.rowcount == 0:
            return jsonify({"message": "Produto não encontrado"}), 404
        
        return jsonify({"message": "Produto editado com sucesso"}), 200

    except Exception as e:
        print(f"Erro ao atualizar produto: {e}")
        return jsonify({"message": "Erro Interno"}), 500

# Apaga Prod.
@app.route('/api/products/remove/<int:product_id>/', methods=['DELETE'])
def remove_product(product_id):

    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM produto WHERE id_prod = %s', (product_id,))
        conn.commit()
        

        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return jsonify({"message": "Produto não encontrado"}), 404

        cursor.close()
        conn.close()

        return jsonify({"message": "Produto removido com sucesso"}), 200

    except Exception as e:
        print(f"Erro ao remover produto: {e}")
        return jsonify({"message": "Erro interno"}), 500       

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)