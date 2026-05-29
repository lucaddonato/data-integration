import json
import psycopg2

with open("/opt/airflow/data/movies.json", "r", encoding="utf-8") as f:
    movie = json.load(f)

conn = psycopg2.connect(
    host="postgres",
    database="movies_db",
    user="admin",
    password="admin"
)

cur = conn.cursor()

cur.execute("""
INSERT INTO movies (
    id,
    title,
    release_date,
    budget,
    revenue,
    vote_average
)
VALUES (%s, %s, %s, %s, %s, %s)
ON CONFLICT (id) DO NOTHING
""", (
    movie["id"],
    movie["title"],
    movie["release_date"],
    movie["budget"],
    movie["revenue"],
    movie["vote_average"]
))

conn.commit()

print("Filme inserido com sucesso")

cur.close()
conn.close()