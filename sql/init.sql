CREATE TABLE IF NOT EXISTS dim_genre (
    genre_id   INTEGER PRIMARY KEY,
    genre_name VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_language (
    language_code VARCHAR(10)  PRIMARY KEY,
    language_name VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS fact_movies (
    movie_id       INTEGER PRIMARY KEY,
    title          VARCHAR(500) NOT NULL,
    original_title VARCHAR(500),
    release_date   DATE,
    budget         BIGINT       DEFAULT 0,
    revenue        BIGINT       DEFAULT 0,
    vote_average   NUMERIC(4,2),
    vote_count     INTEGER      DEFAULT 0,
    popularity     NUMERIC(10,3),
    runtime        INTEGER,
    language_code  VARCHAR(10)  REFERENCES dim_language(language_code),
    overview       TEXT,
    loaded_at      TIMESTAMP    DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS movie_genres (
    movie_id INTEGER REFERENCES fact_movies(movie_id) ON DELETE CASCADE,
    genre_id INTEGER REFERENCES dim_genre(genre_id)  ON DELETE CASCADE,
    PRIMARY KEY (movie_id, genre_id)
);
