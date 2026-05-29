import psycopg2

conn = psycopg2.connect(
    host="postgres",
    database="movies_db",
    user="admin",
    password="admin"
)

cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM movies;")
total = cur.fetchone()[0]

if total == 0:
    raise ValueError("A tabela movies está vazia")

print(f"Validação concluída. Total de filmes na tabela: {total}")

cur.close()
conn.close()