from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
from api import app

CORS(app, origins="http://localhost:5174/") 

def get_conn():
    caminhoBanco = os.path.join(os.path.dirname(__file__), '..', 'db', 'barbalao.db')
    conn = sqlite3.connect(caminhoBanco)
    conn.row_factory = sqlite3.Row
    return conn

# Cria Prod.
@app.route('/api/products/', methods=['POST'])
def create_product():
    try:
        data = request.get_json()

        if data is None:
            return jsonify({"message": "JSON inválido ou ausente"}), 400
    
        name = data.get('nome')
        image = data.get('imagem')
        price = data.get('preco')

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
        new_id = cursor.lastrowid

        conn.close()

        return jsonify({"message": "Produto Criado", "id": new_id}), 201


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
@app.route('/api/produtcs/atualizar/<int:product_id>/', methods=['POST'])
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

        cursor.commit()
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

    