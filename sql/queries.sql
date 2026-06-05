-- Consulta 1: Top 10 filmes por lucro

SELECT
    title,
    (revenue - budget) AS profit
FROM fact_movies
ORDER BY profit DESC
LIMIT 10;


-- Consulta 2: Top 10 filmes mais bem avaliados

SELECT
    title,
    vote_average,
    vote_count
FROM fact_movies
ORDER BY vote_average DESC
LIMIT 10;


-- Consulta 3: Top 10 filmes por receita

SELECT
    title,
    revenue
FROM fact_movies
ORDER BY revenue DESC
LIMIT 10;