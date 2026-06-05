-- Consulta 1: Top 10 filmes por lucro

SELECT
    m.title,
    f.profit
FROM fact_movie_metrics f
JOIN dim_movie m
    ON f.movie_id = m.movie_id
ORDER BY f.profit DESC
LIMIT 10;


-- Consulta 2: Top 10 filmes mais bem avaliados

SELECT
    m.title,
    f.kaggle_score,
    f.vote_average
FROM fact_movie_metrics f
JOIN dim_movie m
    ON f.movie_id = m.movie_id
ORDER BY f.kaggle_score DESC
LIMIT 10;


-- Consulta 3: Top 10 filmes por receita

SELECT
    m.title,
    f.revenue
FROM fact_movie_metrics f
JOIN dim_movie m
    ON f.movie_id = m.movie_id
ORDER BY f.revenue DESC
LIMIT 10;