import psycopg2
# from encrypt import hash_password

while True:
    try:
        conn = psycopg2.connect(
            dbname="banco_barbalao",  
            user="root",       
            password="DdDLJr8BYykOf9hJL9TWXP2eDsF2A8S6",    
            host="dpg-d42kp3i4d50c739qr750-a.oregon-postgres.render.com",            
            port="5432"
        )
        cursor = conn.cursor()

        cursor.execute("DROP TABLE IF EXISTS categoria CASCADE;")
        # cursor.execute("DROP TABLE IF EXISTS products CASCADE")
        conn.commit()


        cursor.execute('''
                            CREATE TABLE IF NOT EXISTS users(
                            iduser SERIAL PRIMARY KEY,
                            nome TEXT NOT NULL UNIQUE,
                            hash TEXT NOT NULL
                    );
                        ''')
        
        # cursor.execute('''
        #                     INSERT INTO users(nome, hash)
        #                     VALUES(%s, %s);
        #             ''', ('EDUARDO', 'Barbalao123'))
        #             # hash_password('Barbalao123')


        # cursor.execute(
        #     '''
        #         CREATE TABLE IF NOT EXISTS categoria(
        #             id_categ        SERIAL PRIMARY KEY,
        #             name_categ      TEXT NOT NULL,
        #             image_categ     TEXT
        #         )
        #     '''
        # )
        cursor.execute(
            '''
                CREATE TABLE IF NOT EXISTS products(
                    id_prod  SERIAL PRIMARY KEY,
                    image   TEXT,
                    name    TEXT NOT NULL,
                    price   REAL NOT NULL
                );
            '''
            # categ_id    INTEGER NOT NULL,

            # FOREIGN KEY(categ_id) REFERENCES  categoria(id_categ)
        )

        
        
        conn.commit()
        conn.close()

    except psycopg2.Error as e: 
        print(f"Erro não legal: {e}")
        continue
