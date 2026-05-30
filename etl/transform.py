import json
import pandas as pd

with open("/opt/airflow/data/movies.json", "r", encoding="utf-8") as f:
    movies = json.load(f)

csv_df = pd.read_csv("/opt/airflow/data/kaggle_movies.csv")

transformed_movies = []

for movie in movies:

    csv_match = csv_df[csv_df["id"] == movie["id"]]

    if csv_match.empty:
        print(f"Filme não encontrado no CSV: {movie['title']}")
        continue

    csv_movie = csv_match.iloc[0]

    transformed_movie = {
        "id": movie["id"],
        "title": movie["title"],
        "release_date": movie["release_date"],
        "budget": movie["budget"],
        "revenue": movie["revenue"],
        "vote_average": movie["vote_average"],
        "original_language": movie["original_language"],
        "status": movie["status"],
        "kaggle_score": float(csv_movie["kaggle_score"]),
        "kaggle_runtime": int(csv_movie["kaggle_runtime"])
    }

    transformed_movies.append(transformed_movie)

with open(
    "/opt/airflow/data/transformed_movies.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        transformed_movies,
        f,
        ensure_ascii=False,
        indent=4
    )

print(f"{len(transformed_movies)} filmes transformados com sucesso")