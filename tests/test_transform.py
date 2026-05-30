import pytest
import pandas as pd

from transform import (
    validate_nulls,
    validate_duplicates,
    validate_ranges,
    extract_genres,
    extract_languages,
    build_movie_genres,
)


# ---------------------------------------------------------------------------
# Fixture auxiliar
# ---------------------------------------------------------------------------

def make_df(**overrides):
    """Retorna um DataFrame de uma linha com valores válidos por padrão."""
    base = {
        "id": 1,
        "title": "Test Movie",
        "vote_average": 7.5,
        "vote_count": 1000,
        "budget": 1_000_000,
        "revenue": 2_000_000,
        "popularity": 50.0,
        "runtime": 120,
    }
    base.update(overrides)
    return pd.DataFrame([base])


# ---------------------------------------------------------------------------
# validate_nulls
# ---------------------------------------------------------------------------

class TestValidateNulls:
    def test_dropa_linha_com_id_nulo(self):
        df = make_df(id=None)
        result = validate_nulls(df)
        assert len(result) == 0

    def test_dropa_linha_com_title_nulo(self):
        df = make_df(title=None)
        result = validate_nulls(df)
        assert len(result) == 0

    def test_mantem_linha_valida(self):
        df = make_df()
        result = validate_nulls(df)
        assert len(result) == 1

    def test_preenche_vote_average_nulo_com_zero(self):
        df = make_df(vote_average=None)
        result = validate_nulls(df)
        assert result.iloc[0]["vote_average"] == 0.0

    def test_preenche_budget_nulo_com_zero(self):
        df = make_df(budget=None)
        result = validate_nulls(df)
        assert result.iloc[0]["budget"] == 0

    def test_preenche_revenue_nulo_com_zero(self):
        df = make_df(revenue=None)
        result = validate_nulls(df)
        assert result.iloc[0]["revenue"] == 0

    def test_dropa_apenas_linha_invalida_mantendo_validas(self):
        df = pd.DataFrame([
            {"id": 1, "title": "Valido", "vote_average": 7.0, "vote_count": 100,
             "budget": 1000, "revenue": 2000, "popularity": 5.0, "runtime": 90},
            {"id": None, "title": "Invalido", "vote_average": 5.0, "vote_count": 50,
             "budget": 500, "revenue": 1000, "popularity": 3.0, "runtime": 80},
        ])
        result = validate_nulls(df)
        assert len(result) == 1
        assert result.iloc[0]["title"] == "Valido"


# ---------------------------------------------------------------------------
# validate_duplicates
# ---------------------------------------------------------------------------

class TestValidateDuplicates:
    def test_remove_duplicata_mantendo_maior_vote_count(self):
        df = pd.DataFrame([
            {"id": 1, "title": "Movie A", "vote_average": 7.0, "vote_count": 500,
             "budget": 0, "revenue": 0, "popularity": 1.0, "runtime": 100},
            {"id": 1, "title": "Movie A (dup)", "vote_average": 6.0, "vote_count": 200,
             "budget": 0, "revenue": 0, "popularity": 1.0, "runtime": 100},
        ])
        result = validate_duplicates(df)
        assert len(result) == 1
        assert result.iloc[0]["vote_count"] == 500

    def test_nao_remove_registros_sem_duplicata(self):
        df = pd.DataFrame([
            {"id": 1, "title": "Movie A", "vote_average": 7.0, "vote_count": 500,
             "budget": 0, "revenue": 0, "popularity": 1.0, "runtime": 100},
            {"id": 2, "title": "Movie B", "vote_average": 8.0, "vote_count": 300,
             "budget": 0, "revenue": 0, "popularity": 2.0, "runtime": 110},
        ])
        result = validate_duplicates(df)
        assert len(result) == 2

    def test_mantém_ordem_descendente_por_vote_count(self):
        df = pd.DataFrame([
            {"id": 1, "title": "A", "vote_count": 100, "vote_average": 7.0,
             "budget": 0, "revenue": 0, "popularity": 1.0, "runtime": 90},
            {"id": 2, "title": "B", "vote_count": 900, "vote_average": 8.0,
             "budget": 0, "revenue": 0, "popularity": 2.0, "runtime": 95},
        ])
        result = validate_duplicates(df)
        assert result.iloc[0]["id"] == 2


# ---------------------------------------------------------------------------
# validate_ranges
# ---------------------------------------------------------------------------

class TestValidateRanges:
    def test_vote_average_acima_de_10_vira_none(self):
        df = make_df(vote_average=11.0)
        result = validate_ranges(df)
        assert result.iloc[0]["vote_average"] is None or pd.isna(result.iloc[0]["vote_average"])

    def test_vote_average_negativo_vira_none(self):
        df = make_df(vote_average=-1.0)
        result = validate_ranges(df)
        assert result.iloc[0]["vote_average"] is None or pd.isna(result.iloc[0]["vote_average"])

    def test_vote_average_valido_permanece_inalterado(self):
        df = make_df(vote_average=8.5)
        result = validate_ranges(df)
        assert result.iloc[0]["vote_average"] == 8.5

    def test_vote_average_nos_limites_0_e_10_eh_valido(self):
        for valor in [0.0, 10.0]:
            df = make_df(vote_average=valor)
            result = validate_ranges(df)
            assert result.iloc[0]["vote_average"] == valor

    def test_budget_negativo_vira_zero(self):
        df = make_df(budget=-500)
        result = validate_ranges(df)
        assert result.iloc[0]["budget"] == 0

    def test_budget_zero_permanece_zero(self):
        df = make_df(budget=0)
        result = validate_ranges(df)
        assert result.iloc[0]["budget"] == 0

    def test_revenue_negativo_vira_zero(self):
        df = make_df(revenue=-1000)
        result = validate_ranges(df)
        assert result.iloc[0]["revenue"] == 0

    def test_runtime_zero_vira_none(self):
        df = make_df(runtime=0)
        result = validate_ranges(df)
        assert result.iloc[0]["runtime"] is None or pd.isna(result.iloc[0]["runtime"])

    def test_runtime_negativo_vira_none(self):
        df = make_df(runtime=-10)
        result = validate_ranges(df)
        assert result.iloc[0]["runtime"] is None or pd.isna(result.iloc[0]["runtime"])

    def test_runtime_valido_permanece_inalterado(self):
        df = make_df(runtime=120)
        result = validate_ranges(df)
        assert result.iloc[0]["runtime"] == 120


# ---------------------------------------------------------------------------
# extract_genres
# ---------------------------------------------------------------------------

class TestExtractGenres:
    def test_extrai_generos_unicos(self):
        raw = [
            {"genres": [{"id": 28, "name": "Action"}, {"id": 18, "name": "Drama"}]},
            {"genres": [{"id": 28, "name": "Action"}]},
        ]
        result = extract_genres(raw)
        ids = {g["genre_id"] for g in result}
        assert ids == {28, 18}
        assert len(result) == 2

    def test_ignora_filmes_sem_genero(self):
        raw = [{"genres": []}, {"genres": None}]
        result = extract_genres([{"genres": []}])
        assert result == []

    def test_retorna_lista_vazia_para_entrada_vazia(self):
        assert extract_genres([]) == []

    def test_estrutura_do_retorno(self):
        raw = [{"genres": [{"id": 12, "name": "Adventure"}]}]
        result = extract_genres(raw)
        assert result[0]["genre_id"] == 12
        assert result[0]["genre_name"] == "Adventure"


# ---------------------------------------------------------------------------
# extract_languages
# ---------------------------------------------------------------------------

class TestExtractLanguages:
    def test_extrai_idiomas_unicos(self):
        raw = [
            {"original_language": "en", "spoken_languages": [{"iso_639_1": "en", "english_name": "English"}]},
            {"original_language": "pt", "spoken_languages": [{"iso_639_1": "pt", "english_name": "Portuguese"}]},
            {"original_language": "en", "spoken_languages": []},
        ]
        result = extract_languages(raw)
        codes = {l["language_code"] for l in result}
        assert codes == {"en", "pt"}
        assert len(result) == 2

    def test_usa_codigo_como_nome_quando_spoken_languages_vazio(self):
        raw = [{"original_language": "ja", "spoken_languages": []}]
        result = extract_languages(raw)
        assert result[0]["language_code"] == "ja"
        assert result[0]["language_name"] == "ja"

    def test_ignora_filmes_sem_original_language(self):
        raw = [{"original_language": None, "spoken_languages": []}]
        result = extract_languages(raw)
        assert result == []


# ---------------------------------------------------------------------------
# build_movie_genres
# ---------------------------------------------------------------------------

class TestBuildMovieGenres:
    def test_gera_relacoes_corretas(self):
        raw = [{"id": 1, "genres": [{"id": 28}, {"id": 18}]}]
        result = build_movie_genres(raw, valid_ids={1})
        assert {"movie_id": 1, "genre_id": 28} in result
        assert {"movie_id": 1, "genre_id": 18} in result
        assert len(result) == 2

    def test_exclui_filmes_fora_de_valid_ids(self):
        raw = [
            {"id": 1, "genres": [{"id": 28}]},
            {"id": 2, "genres": [{"id": 18}]},
        ]
        result = build_movie_genres(raw, valid_ids={1})
        movie_ids = {r["movie_id"] for r in result}
        assert movie_ids == {1}

    def test_retorna_lista_vazia_se_sem_generos(self):
        raw = [{"id": 1, "genres": []}]
        result = build_movie_genres(raw, valid_ids={1})
        assert result == []
