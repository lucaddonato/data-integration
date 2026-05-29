import os
import json
import requests

API_KEY = os.getenv("TMDB_API_KEY")

url = f"https://api.themoviedb.org/3/movie/550?api_key={API_KEY}"

response = requests.get(url)

movie = response.json()

with open("/opt/airflow/data/movies.json", "w", encoding="utf-8") as f:
    json.dump(movie, f, ensure_ascii=False, indent=4)

print("Arquivo salvo com sucesso")