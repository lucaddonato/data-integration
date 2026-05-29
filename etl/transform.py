import json
import pandas as pd

RAW_PATH      = "/opt/airflow/data/raw_movies.json"
CLEAN_PATH    = "/opt/airflow/data/movies_clean.json"
GENRES_PATH   = "/opt/airflow/data/genres.json"
LANGUAGES_PATH = "/opt/airflow/data/languages.json"


def load_raw():
    with open(RAW_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_nulls(df):
    """Regra 1 — Nulos: remove registros sem id ou title; preenche nulos nos demais campos."""
    before = len(df)
    df = df.dropna(subset=["id", "title"])
    dropped = before - len(df)
    if dropped:
        print(f"[transform] Regra 1 (nulos): {dropped} registro(s) removido(s) por id/title nulo")

    df["vote_average"] = df["vote_average"].fillna(0.0)
    df["vote_count"]   = df["vote_count"].fillna(0).astype(int)
    df["budget"]       = df["budget"].fillna(0).astype(int)
    df["revenue"]      = df["revenue"].fillna(0).astype(int)
    df["popularity"]   = df["popularity"].fillna(0.0)
    return df


def validate_duplicates(df):
    """Regra 2 — Duplicidades: ordena por vote_count desc e mantém primeira ocorrência por id."""
    before = len(df)
    df = df.sort_values("vote_count", ascending=False)
    df = df.drop_duplicates(subset="id", keep="first")
    dropped = before - len(df)
    if dropped:
        print(f"[transform] Regra 2 (duplicatas): {dropped} registro(s) duplicado(s) removido(s)")
    else:
        print(f"[transform] Regra 2 (duplicatas): nenhuma duplicata encontrada")
    return df


def validate_ranges(df):
    """Regra 3 — Ranges: corrige valores fora dos limites aceitáveis."""
    # vote_average deve ser [0, 10]
    mask_va = ~df["vote_average"].between(0, 10)
    if mask_va.any():
        print(f"[transform] Regra 3 (ranges): {mask_va.sum()} vote_average(s) fora de [0,10] → None")
        df.loc[mask_va, "vote_average"] = None

    # budget e revenue nao podem ser negativos
    mask_budget = df["budget"] < 0
    if mask_budget.any():
        print(f"[transform] Regra 3 (ranges): {mask_budget.sum()} budget(s) negativo(s) → 0")
        df.loc[mask_budget, "budget"] = 0

    mask_revenue = df["revenue"] < 0
    if mask_revenue.any():
        print(f"[transform] Regra 3 (ranges): {mask_revenue.sum()} revenue(s) negativo(s) → 0")
        df.loc[mask_revenue, "revenue"] = 0

    # runtime deve ser positivo quando presente
    if "runtime" in df.columns:
        mask_runtime = df["runtime"].notna() & (df["runtime"] <= 0)
        if mask_runtime.any():
            print(f"[transform] Regra 3 (ranges): {mask_runtime.sum()} runtime(s) invalido(s) → None")
            df.loc[mask_runtime, "runtime"] = None

    return df


def extract_genres(movies_raw):
    """Extrai todos os pares (genre_id, genre_name) únicos de todos os filmes."""
    genres = {}
    for movie in movies_raw:
        for g in movie.get("genres", []):
            if g.get("id") and g.get("name"):
                genres[g["id"]] = g["name"]
    return [{"genre_id": k, "genre_name": v} for k, v in genres.items()]


def extract_languages(movies_raw):
    """Extrai todos os pares (language_code, language_name) únicos."""
    languages = {}
    for movie in movies_raw:
        code = movie.get("original_language")
        if code:
            # Tenta obter o nome completo a partir de spoken_languages
            name = code
            for lang in movie.get("spoken_languages", []):
                if lang.get("iso_639_1") == code:
                    name = lang.get("english_name", code)
                    break
            languages[code] = name
    return [{"language_code": k, "language_name": v} for k, v in languages.items()]


def build_movie_genres(movies_raw, valid_ids):
    """Monta a lista de relações filme ↔ gênero para a tabela movie_genres."""
    relations = []
    for movie in movies_raw:
        mid = movie.get("id")
        if mid not in valid_ids:
            continue
        for g in movie.get("genres", []):
            if g.get("id"):
                relations.append({"movie_id": mid, "genre_id": g["id"]})
    return relations


def transform():
    raw = load_raw()
    print(f"[transform] {len(raw)} filmes carregados do arquivo bruto")

    # Monta DataFrame com os campos relevantes
    records = []
    for m in raw:
        records.append({
            "id":             m.get("id"),
            "title":          m.get("title"),
            "original_title": m.get("original_title"),
            "release_date":   m.get("release_date") or None,
            "budget":         m.get("budget"),
            "revenue":        m.get("revenue"),
            "vote_average":   m.get("vote_average"),
            "vote_count":     m.get("vote_count"),
            "popularity":     m.get("popularity"),
            "runtime":        m.get("runtime"),
            "language_code":  m.get("original_language"),
            "overview":       m.get("overview"),
        })

    df = pd.DataFrame(records)

    # Aplica as 3 regras de validacao
    df = validate_nulls(df)
    df = validate_duplicates(df)
    df = validate_ranges(df)

    print(f"[transform] {len(df)} filmes após todas as validações")

    valid_ids = set(df["id"].tolist())

    # Salva filmes limpos
    df["id"] = df["id"].astype(int)
    movies_clean = df.where(pd.notnull(df), None).to_dict(orient="records")
    with open(CLEAN_PATH, "w", encoding="utf-8") as f:
        json.dump(movies_clean, f, ensure_ascii=False, indent=2)
    print(f"[transform] movies_clean.json salvo com {len(movies_clean)} registros")

    # Salva dimensoes
    genres = extract_genres(raw)
    with open(GENRES_PATH, "w", encoding="utf-8") as f:
        json.dump(genres, f, ensure_ascii=False, indent=2)
    print(f"[transform] genres.json salvo com {len(genres)} generos")

    languages = extract_languages(raw)
    with open(LANGUAGES_PATH, "w", encoding="utf-8") as f:
        json.dump(languages, f, ensure_ascii=False, indent=2)
    print(f"[transform] languages.json salvo com {len(languages)} idiomas")

    # Salva relacoes filme-genero junto ao clean para uso no load
    movie_genres = build_movie_genres(raw, valid_ids)
    with open("/opt/airflow/data/movie_genres.json", "w", encoding="utf-8") as f:
        json.dump(movie_genres, f, ensure_ascii=False, indent=2)
    print(f"[transform] movie_genres.json salvo com {len(movie_genres)} relacoes")


if __name__ == "__main__":
    transform()
