import os
import json
import requests

API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"
RAW_PATH = "/opt/airflow/data/raw_movies.json"
LOCAL_JSON = "/opt/airflow/data/movies.json"


def fetch_movie_detail(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}?api_key={API_KEY}&language=en-US"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def fetch_popular_movies(pages=2):
    movies = []
    for page in range(1, pages + 1):
        url = f"{BASE_URL}/movie/popular?api_key={API_KEY}&language=en-US&page={page}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        results = response.json().get("results", [])
        movies.extend(results)
        print(f"[extract] Pagina {page} obtida — {len(results)} filmes")
    return movies


def load_local_json():
    with open(LOCAL_JSON, "r", encoding="utf-8") as f:
        movie = json.load(f)
    print(f"[extract] Fonte local: '{movie.get('title')}' (id={movie.get('id')})")
    return [movie]


def extract():
    # Fonte 1: TMDB API — filmes populares (paginas 1 e 2)
    popular = fetch_popular_movies(pages=2)
    popular_ids = {m["id"] for m in popular}

    # Para cada filme popular, busca detalhes completos (genres, budget, runtime, etc.)
    detailed = []
    for movie in popular:
        try:
            detail = fetch_movie_detail(movie["id"])
            detailed.append(detail)
        except Exception as e:
            print(f"[extract] Erro ao buscar detalhe do filme {movie['id']}: {e}")

    # Fonte 2: JSON local (arquivo pre-salvo em data/movies.json)
    local_movies = load_local_json()

    # Mescla: adiciona filme local se ainda nao esta na lista da API
    for movie in local_movies:
        if movie.get("id") not in popular_ids:
            detailed.append(movie)

    print(f"[extract] Total bruto antes da deduplicacao: {len(detailed)} filmes")

    # Deduplicacao simples por id (mantem primeira ocorrencia)
    seen = set()
    unique = []
    for movie in detailed:
        mid = movie.get("id")
        if mid is not None and mid not in seen:
            seen.add(mid)
            unique.append(movie)

    print(f"[extract] Total apos deduplicacao: {len(unique)} filmes")

    with open(RAW_PATH, "w", encoding="utf-8") as f:
        json.dump(unique, f, ensure_ascii=False, indent=2)

    print(f"[extract] raw_movies.json salvo com {len(unique)} registros")


if __name__ == "__main__":
    extract()
