import json
import pandas as pd

with open("/opt/airflow/data/movies.json", "r", encoding="utf-8") as f:
    movie = json.load(f)

csv_df = pd.read_csv("/opt/airflow/data/kaggle_movies.csv")

csv_movie = csv_df[csv_df["id"] == movie["id"]].iloc[0]

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

with open("/opt/airflow/data/transformed_movies.json", "w", encoding="utf-8") as f:
    json.dump(transformed_movie, f, ensure_ascii=False, indent=4)

print("Transformação concluída")
print(transformed_movie)