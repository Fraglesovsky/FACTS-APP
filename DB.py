import psycopg2
from datetime import datetime
from urllib.parse import urlparse, parse_qs

connection_string = "postgresql://facts_user:WBpCkxmaFL5MtkojXePDA4RTic2aEgU6@dpg-cvapvktrie7s739801vg-a.frankfurt-postgres.render.com/facts?ssl=true"
url = urlparse(connection_string)

connection_details = {
    "user": url.username,
    "password": url.password,
    "host": url.hostname,
    "port": url.port or 5432,
    "database": url.path.lstrip('/'),
    "ssl": parse_qs(url.query).get("ssl", ["false"])[0]
}


def db_conn():
    try:
        conn = psycopg2.connect(
            host=connection_details["host"],
            database=connection_details["database"],
            user=connection_details["user"],
            password=connection_details["password"],
            sslmode="require"
        )
        cur = conn.cursor()
        cur.execute('''
            CREATE SCHEMA IF NOT EXISTS main;
            CREATE TABLE IF NOT EXISTS main.facts (
                id SERIAL PRIMARY KEY,
                fakt TEXT,
                lang TEXT,        
                created TIMESTAMP,
                UNIQUE(fakt)
            )
        ''')
        conn.commit()  # Zatwierdź zmiany
        conn.close()
        return "db_conn executed successfully"
    except Exception as e:
        return f"Error in db_conn: {e}"


def save_fact(fact, lang="en"):
    try:
        conn = psycopg2.connect(
            host=connection_details["host"],
            database=connection_details["database"],
            user=connection_details["user"],
            password=connection_details["password"],
            sslmode="require"
        )
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO main.facts (fakt, lang, created) VALUES (%s, %s, %s)", (fact, lang, datetime.now()))
            conn.commit()  # Zatwierdź zmiany
        except psycopg2.IntegrityError:
            print("Duplikat - fakt już istnieje w bazie.")
        finally:
            conn.close()
    except Exception as e:
        print(f"Błąd podczas zapisu faktu: {e}")


def fact_exists(content: str) -> bool:
    try:
        conn = psycopg2.connect(
            host=connection_details["host"],
            database=connection_details["database"],
            user=connection_details["user"],
            password=connection_details["password"],
            sslmode="require"
        )
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM main.facts WHERE fakt=%s", (content,))
        exists = cur.fetchone() is not None
        conn.close()
        return exists
    except Exception as e:
        print(f"Błąd podczas sprawdzania faktu: {e}")
db_conn()


