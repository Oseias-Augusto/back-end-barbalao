import sqlite3
from encrypt import hash_password
hashC = hash_password('Barbalao123')
try:
    conn = sqlite3.connect('barbalao.db')

    cursor = conn.cursor()
    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS users(
                        iduser INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        nome TEXT NOT NULL UNIQUE,
                        hash TEXT NOT NULL
                );
                    ''')
    
    cursor.execute('''
                        INSERT INTO users(nome, hash)
                        VALUES(?, ?);
                ''', ('Eduardo', hashC))


    cursor.execute(
        '''
            CREATE TABLE IF NOT EXISTS categoria(
                id_categ        INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                name_categ      TEXT NOT NULL,
                image_categ     TEXT
            )
        '''
    )
    cursor.execute(
        '''
            CREATE TABLE IF NOT EXISTS products(
                idprod  INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                image   TEXT,
                name    TEXT NOT NULL,
                price   REAL NOT NULL
            );
        '''
    )

    
    
    conn.commit()
    conn.close()

except sqlite3.Error as e: 
    print(f"Erro não legal: {e}")