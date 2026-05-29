CREATE TABLE IF NOT EXISTS dim_movie (
    movie_id INTEGER PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    original_language VARCHAR(10),
    status VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS dim_release_date (
    date_id INTEGER PRIMARY KEY,
    release_date DATE NOT NULL,
    release_year INTEGER NOT NULL,
    release_month INTEGER NOT NULL,
    release_day INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_movie_metrics (
    movie_id INTEGER NOT NULL,
    date_id INTEGER NOT NULL,
    budget BIGINT NOT NULL,
    revenue BIGINT NOT NULL,
    profit BIGINT NOT NULL,
    vote_average NUMERIC(4,2) NOT NULL,
    kaggle_score NUMERIC(4,2) NOT NULL,
    kaggle_runtime INTEGER NOT NULL,

    PRIMARY KEY (movie_id, date_id),

    CONSTRAINT fk_movie
        FOREIGN KEY (movie_id)
        REFERENCES dim_movie(movie_id),

    CONSTRAINT fk_release_date
        FOREIGN KEY (date_id)
        REFERENCES dim_release_date(date_id)
);