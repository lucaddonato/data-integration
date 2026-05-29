CREATE TABLE IF NOT EXISTS movies (
    id INTEGER PRIMARY KEY,
    title VARCHAR(255),
    release_date DATE,
    budget BIGINT,
    revenue BIGINT,
    vote_average NUMERIC(4,2)
);