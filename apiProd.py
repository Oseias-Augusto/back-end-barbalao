from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app, origins=["http://localhost:5174/",
        "https://barbalao.vercel.app"]) 

def get_conn():
    conn = sqlite3.connect('barbalao.db')
    conn.row_factory = sqlite3.Row
    return conn

# Cria Prod.
@app.route('/api/products/', methods=['POST'])
def create_product():
    try:
        data = request.get_json()
        print("1")

        if data is None:
            return jsonify({"message": "JSON inválido ou ausente"}), 400
        
    
        name = data.get('nome')
        image = data.get('imagem')
        price = data.get('preco')
        print("2")

        if not name or price is None:
            return jsonify({"message": "Campos obrigatórios: name e price"}), 400

        conn = get_conn()
        cursor = conn.cursor()

        cursor.execute(
            '''
             INSERT INTO products(name, price, image)
             VALUES (?, ?, ?)
            ''', (name, price, image))
        
        conn.commit()
        print(cursor.lastrowid)
        new_id = cursor.lastrowid

        conn.close()
        
        return jsonify({
                    "header": {
                        "Access-Control-Allow-Headers",
                        "Origin, X-Requested-With, Content-Type, Accept"
                    },
                    
                    "data": {
                        "items": [
                                {
                                    "id": new_id,
                                    "message": "Produto Criado",
                                    "value": 201
                                }
                        ]
            
            
            }}), 201


    except Exception as e:
        print(f"Erro ao criar produto: {e}")
        return jsonify({"message": "Erro interno"}), 500

# Pega Prod.
@app.route('/api/products/', methods=['GET'])
def list_products():
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute('''SELECT idprod, image, name, price FROM products;''')
        rows = cursor.fetchall()

        conn.close()

        products = [dict(row) for row in rows]

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
            cursor.execute('UPDATE products SET name = ? WHERE idprod = ?;', (product_name, product_id))
        if product_image:
            cursor.execute('UPDATE products SET image = ? WHERE idprod = ?;', (product_image, product_id))
        if product_price:
            cursor.execute('UPDATE products SET price = ? WHERE idprod = ?;', (product_image, product_id))

        conn.commit()
        cursor.close()

        if cursor.rowcount == 0:
            return jsonify({"message": "Produto não encontrado"}), 404
        
        return jsonify({"message": "Produto editado com sucesso"}), 200

    except Exception as e:
        print(f"Erro ao atualizar produto: {e}")
        return jsonify({"message": "Erro Interno"}), 500

# Apaga Prod.
@app.route('/api/products/remove/<int:product_id>/', methods=['POST'])
def remove_product(product_id):
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM products WHERE idprod = ?', (product_id,))
        conn.commit()
        conn.close()

        if cursor.rowcount == 0:
            return jsonify({"message": "Produto não encontrado"}), 404

        return jsonify({"message": "Produto removido com sucesso"}), 200

    except Exception as e:
        print(f"Erro ao remover produto: {e}")
        return jsonify({"message": "Erro interno"}), 500       

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Render define PORT
    app.run(host="0.0.0.0", port=port)

