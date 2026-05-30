import os
import json
import requests

API_KEY = os.getenv("TMDB_API_KEY")

movies_names = [
    "The Shawshank Redemption",
    "The Godfather",
    "The Godfather Part II",
    "The Dark Knight",
    "Pulp Fiction",
    "Fight Club",
    "Forrest Gump",
    "Schindler's List",
    "Goodfellas",
    "The Green Mile",
    "The Lord of the Rings: The Return of the King",
    "Inception",
    "Interstellar",
    "Parasite",
    "Whiplash",
    "The Prestige",
    "Se7en",
    "The Silence of the Lambs",
    "Saving Private Ryan",
    "Gladiator"
]

movies = []

for movie_name in movies_names:

    url = (
        f"https://api.themoviedb.org/3/search/movie"
        f"?api_key={API_KEY}"
        f"&query={movie_name}"
    )

    response = requests.get(url)

    if response.status_code != 200:
        print(f"Erro ao buscar {movie_name}")
        continue

    data = response.json()

    if not data.get("results"):
        print(f"Filme não encontrado: {movie_name}")
        continue

    movie_id = data["results"][0]["id"]

    details_url = (
        f"https://api.themoviedb.org/3/movie/{movie_id}"
        f"?api_key={API_KEY}"
    )

    details = requests.get(details_url).json()

    movies.append(details)

with open(
    "/opt/airflow/data/movies.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        movies,
        f,
        ensure_ascii=False,
        indent=4
    )

print(f"{len(movies)} filmes extraídos com sucesso")