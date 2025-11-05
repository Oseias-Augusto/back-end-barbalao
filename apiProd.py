from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os

app = Flask(__name__)
CORS(app, origins=[
        "https://localhost:5174/",
        "https://barbalao.vercel.app",
        "https://supreme-carnival-x5xvwq7494qxh6r7j-5173.app.github.dev"
]) 


def get_conn():
    conn = psycopg2.connect(
            dbname="banco_barbalao",  
            user="root",       
            password="DdDLJr8BYykOf9hJL9TWXP2eDsF2A8S6",    
            host="dpg-d42kp3i4d50c739qr750-a.oregon-postgres.render.com",            
            port="5432"      
    )
    return conn

@app.after_request
def add_header(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Access-Control-Allow-Headers"] = "Origin, X-Requested-With, Content-Type, Accept"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


# Cria Prod.
@app.route('/api/products/', methods=['POST'])
def create_product():
    try:
        data = request.get_json()
        print("Dados recebidos:", data)

        if data is None:
            print("JSON ausente ou inválido")
            return jsonify({"message": "JSON inválido ou ausente"}), 400
        
        name = data.get('nome')
        image = data.get('imagem')
        price = data.get('preco')
        # categ_id = data.get('categ_id')

        print(f"Nome: {name}, Preço: {price}, Imagem: {type(image)}")

        if not name or price is None:
            print("Campos obrigatórios ausentes")
            return jsonify({"message": "Campos obrigatórios: name e price"}), 400

        conn = get_conn()
        cursor = conn.cursor()

        cursor.execute(
            '''
             INSERT INTO products(name, price, image)
             VALUES (%s, %s, %s)
             RETURNING id_prod
            ''', (name, float(price), image)
        )
        
        conn.commit()
        new_id = cursor.fetchone()[0]
        print("Produto criado com ID:", new_id)

        conn.close()
        
        return jsonify({"message": "Produto Criado", "ID" : new_id}), 201

    except Exception as e:
        print(f"Erro ao criar produto: {e}")
        return jsonify({"message": f"Erro interno: {str(e)}"}), 500


# Pega Prod.
@app.route('/api/products/', methods=['GET'])
def list_products():
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute('''SELECT id_prod, image, name, price FROM products;''')
        rows = cursor.fetchall()

        conn.close()

        products = [
            {
                'id_prod': row[0],
                'image': row[1],
                'name': row[2],
                'price': row[3]
            } for row in rows
        ]

        return jsonify(products), 200
    
    except Exception as e:
        print(f"Erro ao criar produto: {e}")
        return jsonify({"message": "Erro Interno"}), 500

# Atualizar Prod.
@app.route('/api/products/atualizar/<int:product_id>/', methods=['POST'])
def update_products(product_id, product_name = None, product_image = None, product_price = None):
    try:
        conn = get_conn()
        cursor = conn.cursor()
        if product_name:
            cursor.execute('UPDATE products SET name = %s WHERE id_prod = %s;', (product_name, product_id))
        if product_image:
            cursor.execute('UPDATE products SET image = %s WHERE id_prod = %s;', (product_image, product_id))
        if product_price:
            cursor.execute('UPDATE products SET price = %s WHERE id_prod = %s;', (product_image, product_id))

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
        cursor.execute('DELETE FROM products WHERE id_prod = %s', (product_id,))
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

