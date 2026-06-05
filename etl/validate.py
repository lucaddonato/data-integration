import os
import sys
import psycopg2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from logger import get_logger

log = get_logger("validate")


def get_connection():
    return psycopg2.connect(
        host="postgres",
        database="movies_db",
        user="admin",
        password="admin"
    )


def check(cur, description, query, expected=0):
    """Executa a query, compara com expected e levanta ValueError se falhar."""
    cur.execute(query)
    result = cur.fetchone()[0]
    if result != expected:
        log.error(f"FALHA — {description}: resultado={result}, esperado={expected}")
        raise ValueError(f"Validacao falhou: {description}")
    log.info(f"OK — {description}")


def validate():
    log.info("Iniciando validacoes pos-carga")

    conn = get_connection()
    try:
        cur = conn.cursor()

        # Regra 1: Nenhum titulo nulo em fact_movies
        check(
            cur,
            "Sem nulos em title (fact_movies)",
            "SELECT COUNT(*) FROM fact_movies WHERE title IS NULL"
        )

        # Regra 2: Nenhuma duplicata de movie_id em fact_movies
        check(
            cur,
            "Sem duplicatas de movie_id (fact_movies)",
            "SELECT COUNT(*) - COUNT(DISTINCT movie_id) FROM fact_movies"
        )

        # Regra 3: vote_average dentro do range [0, 10]
        check(
            cur,
            "vote_average dentro de [0, 10] (fact_movies)",
            "SELECT COUNT(*) FROM fact_movies WHERE vote_average IS NOT NULL AND vote_average NOT BETWEEN 0 AND 10"
        )

        # Regra 4: Integridade referencial movie_genres → dim_genre
        check(
            cur,
            "Integridade referencial movie_genres → dim_genre",
            """
            SELECT COUNT(*)
            FROM movie_genres mg
            LEFT JOIN dim_genre dg ON mg.genre_id = dg.genre_id
            WHERE dg.genre_id IS NULL
            """
        )

        # Totais finais
        cur.execute("SELECT COUNT(*) FROM fact_movies")
        total_movies = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM dim_genre")
        total_genres = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM dim_language")
        total_languages = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM movie_genres")
        total_relations = cur.fetchone()[0]

        log.info(
            f"Resumo: {total_movies} filmes | "
            f"{total_genres} generos | "
            f"{total_languages} idiomas | "
            f"{total_relations} relacoes filme-genero"
        )

    except Exception as e:
        log.error(f"Validacao encerrada com erro: {e}")
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    validate()
