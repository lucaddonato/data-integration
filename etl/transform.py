import json

with open("/opt/airflow/data/movies.json", "r", encoding="utf-8") as f:
    movie = json.load(f)

print(movie["id"])
print(movie["title"])
print(movie["release_date"])
print(movie["budget"])
print(movie["revenue"])
print(movie["vote_average"])