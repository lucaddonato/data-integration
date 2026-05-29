import json
import psycopg2

with open("/opt/airflow/data/transformed_movies.json", "r", encoding="utf-8") as f:
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
    vote_average,
    kaggle_score,
    kaggle_runtime
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (id) DO UPDATE SET
    title = EXCLUDED.title,
    release_date = EXCLUDED.release_date,
    budget = EXCLUDED.budget,
    revenue = EXCLUDED.revenue,
    vote_average = EXCLUDED.vote_average,
    kaggle_score = EXCLUDED.kaggle_score,
    kaggle_runtime = EXCLUDED.kaggle_runtime
""", (
    movie["id"],
    movie["title"],
    movie["release_date"],
    movie["budget"],
    movie["revenue"],
    movie["vote_average"],
    movie["kaggle_score"],
    movie["kaggle_runtime"]
))

conn.commit()

print("Filme integrado inserido com sucesso")

cur.close()
conn.close()