import psycopg2


conn = psycopg2.connect(
    host="postgres",
    database="movies_db",
    user="admin",
    password="admin"
)

cur = conn.cursor()


cur.execute("SELECT COUNT(*) FROM fact_movie_metrics;")
total = cur.fetchone()[0]

if total == 0:
    raise ValueError("Validação falhou: a tabela fato está vazia")


cur.execute("""
SELECT COUNT(*)
FROM fact_movie_metrics
WHERE budget < 0
   OR revenue < 0
   OR profit < 0
   OR kaggle_runtime < 0;
""")
invalid_ranges = cur.fetchone()[0]

if invalid_ranges > 0:
    raise ValueError("Validação falhou: existem valores negativos nas métricas")


cur.execute("""
SELECT COUNT(*)
FROM fact_movie_metrics f
LEFT JOIN dim_movie d
    ON f.movie_id = d.movie_id
WHERE d.movie_id IS NULL;
""")
missing_movies = cur.fetchone()[0]

if missing_movies > 0:
    raise ValueError("Validação falhou: existem filmes na fato sem dimensão correspondente")


print("Validações concluídas com sucesso")
print(f"Total de registros validados: {total}")


cur.close()
conn.close()