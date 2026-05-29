import json
import psycopg2
from datetime import datetime


with open("/opt/airflow/data/transformed_movies.json", "r", encoding="utf-8") as f:
    movie = json.load(f)


release_date = datetime.strptime(movie["release_date"], "%Y-%m-%d").date()
date_id = int(release_date.strftime("%Y%m%d"))
profit = int(movie["revenue"]) - int(movie["budget"])


conn = psycopg2.connect(
    host="postgres",
    database="movies_db",
    user="admin",
    password="admin"
)

cur = conn.cursor()


cur.execute("""
INSERT INTO dim_movie (
    movie_id,
    title,
    original_language,
    status
)
VALUES (%s, %s, %s, %s)
ON CONFLICT (movie_id) DO UPDATE SET
    title = EXCLUDED.title,
    original_language = EXCLUDED.original_language,
    status = EXCLUDED.status;
""", (
    movie["id"],
    movie["title"],
    movie.get("original_language"),
    movie.get("status")
))


cur.execute("""
INSERT INTO dim_release_date (
    date_id,
    release_date,
    release_year,
    release_month,
    release_day
)
VALUES (%s, %s, %s, %s, %s)
ON CONFLICT (date_id) DO UPDATE SET
    release_date = EXCLUDED.release_date,
    release_year = EXCLUDED.release_year,
    release_month = EXCLUDED.release_month,
    release_day = EXCLUDED.release_day;
""", (
    date_id,
    release_date,
    release_date.year,
    release_date.month,
    release_date.day
))


cur.execute("""
INSERT INTO fact_movie_metrics (
    movie_id,
    date_id,
    budget,
    revenue,
    profit,
    vote_average,
    kaggle_score,
    kaggle_runtime
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (movie_id, date_id) DO UPDATE SET
    budget = EXCLUDED.budget,
    revenue = EXCLUDED.revenue,
    profit = EXCLUDED.profit,
    vote_average = EXCLUDED.vote_average,
    kaggle_score = EXCLUDED.kaggle_score,
    kaggle_runtime = EXCLUDED.kaggle_runtime;
""", (
    movie["id"],
    date_id,
    movie["budget"],
    movie["revenue"],
    profit,
    movie["vote_average"],
    movie["kaggle_score"],
    movie["kaggle_runtime"]
))


conn.commit()

print("Carga dimensional concluída com sucesso")
print(f"Filme: {movie['title']} | Data ID: {date_id} | Lucro: {profit}")

cur.close()
conn.close()