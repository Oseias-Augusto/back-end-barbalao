import psycopg2
from encrypt import hash_password

while True:
    try:
        conn = psycopg2.connect(
            host="postgresql://root:DdDLJr8BYykOf9hJL9TWXP2eDsF2A8S6@dpg-d42kp3i4d50c739qr750-a.oregon-postgres.render.com/banco_barbalao",
            port="5432",
            database="banco_barbalao",
            user="root",
            password="DdDLJr8BYykOf9hJL9TWXP2eDsF2A8S6"
        )
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
                    ''', ('Eduardo', hash_password('Barbalao123')))


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
                    id_prod  INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    image   TEXT,
                    name    TEXT NOT NULL,
                    price   REAL NOT NULL,
                    categ_id    INTEGER NOT NULL,

                    FOREIGN KEY(categ_id) REFERENCES  categoria(id_categ)
                );
            '''
        )

        
        
        conn.commit()
        conn.close()

    except psycopg2.Error as e: 
        print(f"Erro não legal: {e}")
        continue
