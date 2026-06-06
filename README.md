# Pipeline de Integração de Dados — TMDB Movies

Projeto semestral da disciplina **Data Integration** (ESPM — Sistemas de Informação, 2026.1).

# Link YouTube
https://youtu.be/u8ZLy42W2tw

Pipeline ETL completo que extrai dados de filmes de duas fontes heterogêneas, aplica validações de qualidade, transforma e carrega em um banco de dados analítico PostgreSQL, orquestrado pelo Apache Airflow.

---

## Fontes de Dados

| Fonte | Tipo | Descrição |
|---|---|---|
| [TMDB API](https://developer.themoviedb.org/) | API REST | Filmes populares via `/movie/popular` (pág. 1–2) + detalhes por `/movie/{id}` |
| `data/movies.json` | JSON local | Arquivo pré-salvo com dados detalhados de um filme (Fight Club, id=550) |

---

## Arquitetura

```mermaid
flowchart LR
    A([TMDB API\n/movie/popular]) -->|requests| E[extract.py]
    B([movies.json\nJSON local]) -->|json.load| E
    E -->|raw_movies.json| T[transform.py]
    T -->|movies_clean.json\ngenres.json\nlanguages.json| L[load.py]
    L -->|psycopg2| P[(PostgreSQL\nmovies_db)]
    P --> V[validate.py]

    subgraph "Airflow DAG — movies_etl_pipeline"
        E --> T --> L --> V
    end
```

---

## Modelo de Dados

```
dim_language         dim_genre
──────────────       ──────────────
language_code  PK    genre_id  PK
language_name        genre_name

fact_movies
──────────────────────────────
movie_id       PK
title          NOT NULL
original_title
release_date
budget
revenue
vote_average
vote_count
popularity
runtime
language_code  FK → dim_language
overview
loaded_at

movie_genres  (bridge)
──────────────────────────────
movie_id  FK → fact_movies
genre_id  FK → dim_genre
```

---

## Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) 24+
- [Docker Compose](https://docs.docker.com/compose/) (incluso no Docker Desktop)
- Chave de API gratuita do [TMDB](https://www.themoviedb.org/settings/api)

---

## Execução passo a passo

### 1. Clone o repositório

```bash
git clone <url-do-repositorio>
cd data-integration
```

### 2. Configure a chave da API

Crie o arquivo `.env` na raiz do projeto:

```bash
echo "TMDB_API_KEY=sua_chave_aqui" > .env
```

### 3. Suba os contêineres

```bash
docker compose up --build
```

Aguarde até ver a mensagem do scheduler do Airflow nos logs (cerca de 1–2 minutos na primeira execução).

### 4. Acesse o Airflow

Abra [http://localhost:8080](http://localhost:8080) no navegador.

| Campo | Valor |
|---|---|
| Usuário | `admin` |
| Senha | `admin` |

### 5. Execute a DAG

1. Localize a DAG **`movies_etl_pipeline`** na lista.
2. Clique no botão **▶ Trigger DAG** (canto superior direito).
3. Acompanhe as tasks no **Graph View** — todas devem ficar verdes.

### 6. Verifique os dados no Postgres

Conecte-se ao banco com qualquer cliente SQL (DBeaver, psql, etc.):

```
Host:     localhost
Porta:    5432
Banco:    movies_db
Usuário:  admin
Senha:    admin
```

Ou via linha de comando:

```bash
docker exec -it postgres_movies psql -U admin -d movies_db
```

---

## Consultas de valor

### 1. Top 10 filmes por receita

```sql
SELECT title, revenue, budget,
       ROUND((revenue - budget) / NULLIF(budget, 0)::numeric * 100, 1) AS roi_pct
FROM fact_movies
WHERE budget > 0
ORDER BY revenue DESC
LIMIT 10;
```

### 2. Gêneros com mais filmes

```sql
SELECT dg.genre_name, COUNT(*) AS total_filmes
FROM movie_genres mg
JOIN dim_genre dg ON mg.genre_id = dg.genre_id
GROUP BY dg.genre_name
ORDER BY total_filmes DESC;
```

### 3. Média de avaliação por idioma original

```sql
SELECT dl.language_name, COUNT(*) AS filmes,
       ROUND(AVG(fm.vote_average), 2) AS media_nota
FROM fact_movies fm
JOIN dim_language dl ON fm.language_code = dl.language_code
GROUP BY dl.language_name
ORDER BY media_nota DESC;
```

---

## Validações de qualidade

Implementadas em `etl/transform.py` (pré-carga) e `etl/validate.py` (pós-carga):

| # | Regra | Onde | Ação |
|---|---|---|---|
| 1 | `id` ou `title` nulos | transform | Remove o registro |
| 2 | `movie_id` duplicado | transform | Mantém o de maior `vote_count` |
| 3 | `vote_average` fora de [0, 10] | transform | Seta `NULL` |
| 4 | `budget` ou `revenue` negativos | transform | Seta `0` |
| 5 | Sem `title` nulo no banco | validate | Levanta erro se falhar |
| 6 | Sem duplicatas no banco | validate | Levanta erro se falhar |
| 7 | `vote_average` em range no banco | validate | Levanta erro se falhar |
| 8 | Integridade referencial `movie_genres → dim_genre` | validate | Levanta erro se falhar |

---

## Logging

Todos os módulos ETL utilizam um logger estruturado em JSON definido em `etl/logger.py`. Cada linha de log é um objeto JSON com os campos `timestamp`, `level`, `logger` e `message`.

Exemplos reais produzidos pela DAG:

```json
{"timestamp": "2026-05-24T14:32:01.123456+00:00", "level": "INFO", "logger": "extract", "message": "Pagina 1 obtida — 20 filmes"}
{"timestamp": "2026-05-24T14:32:02.456789+00:00", "level": "WARNING", "logger": "extract", "message": "Falha ao buscar detalhe do filme id=12345: ..."}
{"timestamp": "2026-05-24T14:32:05.789012+00:00", "level": "INFO", "logger": "transform", "message": "Regra 2 (duplicatas): nenhuma duplicata encontrada"}
{"timestamp": "2026-05-24T14:32:06.012345+00:00", "level": "WARNING", "logger": "transform", "message": "Regra 1 (nulos): 2 registro(s) removido(s) por id/title nulo"}
{"timestamp": "2026-05-24T14:32:10.345678+00:00", "level": "INFO", "logger": "load", "message": "fact_movies: 41 filme(s) processado(s)"}
{"timestamp": "2026-05-24T14:32:12.678901+00:00", "level": "ERROR", "logger": "validate", "message": "FALHA — Sem duplicatas de movie_id: resultado=2, esperado=0"}
```

Os logs ficam visíveis diretamente nos **Task Logs** do Airflow (aba *Log* de cada task no Graph View).

---

## Testes automatizados

As funções puras de `etl/transform.py` são cobertas por testes unitários em `tests/test_transform.py` usando **pytest**.

### Cobertura

| Classe de teste | Funções testadas |
|---|---|
| `TestValidateNulls` | Drop por `id`/`title` nulo; fill de `vote_average`, `budget`, `revenue` |
| `TestValidateDuplicates` | Remoção de duplicata; mantém registro com maior `vote_count` |
| `TestValidateRanges` | Limites de `vote_average` [0,10]; `budget`/`revenue` negativos; `runtime` inválido |
| `TestExtractGenres` | Deduplicação de gêneros; estrutura do retorno |
| `TestExtractLanguages` | Deduplicação de idiomas; fallback de nome quando `spoken_languages` vazio |
| `TestBuildMovieGenres` | Filtro por `valid_ids`; ausência de gêneros |

### Como executar

Com Python e dependências instaladas localmente:

```bash
pip install pandas pytest
pytest tests/ -v
```

Ou dentro do contêiner Airflow (após `docker compose up`):

```bash
docker exec -it airflow pytest /opt/airflow/tests/ -v
```

---

## Estrutura do repositório

```
data-integration/
├── dags/
│   └── teste-1.py            # DAG do Airflow
├── etl/
│   ├── logger.py             # Logger estruturado compartilhado
│   ├── extract.py            # Extração (TMDB API + JSON local)
│   ├── transform.py          # Transformação e validações
│   ├── load.py               # Carga no PostgreSQL
│   └── validate.py           # Validações pós-carga
├── tests/
│   ├── conftest.py           # Configuração de path para pytest
│   └── test_transform.py     # 27 testes unitários das funções de transformação
├── sql/
│   └── init.sql              # Schema dimensional (criado automaticamente)
├── data/
│   └── movies.json           # Fonte local (seed)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env                      # NÃO commitar — contém a chave de API
└── .gitignore
```

---

## Stack técnica

| Camada | Ferramenta | Versão |
|---|---|---|
| Linguagem | Python | 3.10 |
| Conteinerização | Docker + Docker Compose | 24+ |
| Orquestração | Apache Airflow | 2.8.4 |
| Banco de dados | PostgreSQL | 15 |
| Bibliotecas | pandas, requests, psycopg2-binary, pytest | — |

---

## Uso de Inteligência Artificial

Claude (Anthropic) foi utilizado para revisar a arquitetura do pipeline, corrigir bugs de orquestração no `docker-compose.yml` e sugerir a estrutura do modelo dimensional.
