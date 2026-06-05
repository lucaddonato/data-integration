import os
import sys
import json
import psycopg2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from logger import get_logger

log = get_logger("load")

CLEAN_PATH     = "/opt/airflow/data/movies_clean.json"
GENRES_PATH    = "/opt/airflow/data/genres.json"
LANGUAGES_PATH = "/opt/airflow/data/languages.json"
RELATIONS_PATH = "/opt/airflow/data/movie_genres.json"


def get_connection():
    return psycopg2.connect(
        host="postgres",
        database="movies_db",
        user="admin",
        password="admin"
    )


def load_genres(cur, genres):
    for g in genres:
        cur.execute(
            "INSERT INTO dim_genre (genre_id, genre_name) VALUES (%s, %s) ON CONFLICT DO NOTHING",
            (g["genre_id"], g["genre_name"])
        )
    log.info(f"dim_genre: {len(genres)} genero(s) processado(s)")


def load_languages(cur, languages):
    for lang in languages:
        cur.execute(
            "INSERT INTO dim_language (language_code, language_name) VALUES (%s, %s) ON CONFLICT DO NOTHING",
            (lang["language_code"], lang["language_name"])
        )
    log.info(f"dim_language: {len(languages)} idioma(s) processado(s)")


def load_movies(cur, movies):
    for m in movies:
        cur.execute("""
            INSERT INTO fact_movies (
                movie_id, title, original_title, release_date,
                budget, revenue, vote_average, vote_count,
                popularity, runtime, language_code, overview
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (movie_id) DO UPDATE SET
                title          = EXCLUDED.title,
                original_title = EXCLUDED.original_title,
                release_date   = EXCLUDED.release_date,
                budget         = EXCLUDED.budget,
                revenue        = EXCLUDED.revenue,
                vote_average   = EXCLUDED.vote_average,
                vote_count     = EXCLUDED.vote_count,
                popularity     = EXCLUDED.popularity,
                runtime        = EXCLUDED.runtime,
                language_code  = EXCLUDED.language_code,
                overview       = EXCLUDED.overview,
                loaded_at      = NOW()
        """, (
            int(m.get("movie_id") or m["id"]),
            m.get("title"),
            m.get("original_title"),
            m.get("release_date"),
            m.get("budget") or 0,
            m.get("revenue") or 0,
            m.get("vote_average"),
            m.get("vote_count") or 0,
            m.get("popularity"),
            m.get("runtime"),
            m.get("language_code"),
            m.get("overview"),
        ))
    log.info(f"fact_movies: {len(movies)} filme(s) processado(s)")


def load_movie_genres(cur, relations):
    for rel in relations:
        cur.execute(
            "INSERT INTO movie_genres (movie_id, genre_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
            (rel["movie_id"], rel["genre_id"])
        )
    log.info(f"movie_genres: {len(relations)} relacao(oes) processada(s)")


def load():
    log.info("Iniciando carga no PostgreSQL")

    with open(GENRES_PATH, "r", encoding="utf-8") as f:
        genres = json.load(f)
    with open(LANGUAGES_PATH, "r", encoding="utf-8") as f:
        languages = json.load(f)
    with open(CLEAN_PATH, "r", encoding="utf-8") as f:
        movies = json.load(f)
    with open(RELATIONS_PATH, "r", encoding="utf-8") as f:
        relations = json.load(f)

    conn = get_connection()
    try:
        cur = conn.cursor()

        # Ordem importa: dimensoes antes do fato, fato antes do bridge
        load_genres(cur, genres)
        load_languages(cur, languages)
        load_movies(cur, movies)
        load_movie_genres(cur, relations)

        conn.commit()
        log.info("Carga concluida com sucesso")
    except Exception as e:
        conn.rollback()
        log.error(f"Erro durante a carga — rollback efetuado: {e}")
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    load()
