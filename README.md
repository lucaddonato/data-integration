# Data Integration - Movie ETL Pipeline

## Descrição do Projeto

Este projeto implementa um pipeline ETL (Extract, Transform, Load) para integração de dados de filmes utilizando Python, Docker, Apache Airflow e PostgreSQL.

O objetivo é coletar informações de filmes a partir de duas fontes de dados heterogêneas, realizar transformações e validações de qualidade e armazenar os dados em um banco PostgreSQL utilizando modelagem dimensional.

---

## Fontes de Dados

### Fonte 1 - TMDB API

API utilizada para obtenção dos detalhes dos filmes:

* Título
* Data de lançamento
* Orçamento
* Receita
* Nota média
* Idioma original
* Status do filme

### Fonte 2 - CSV

Arquivo:

```text
data/kaggle_movies.csv
```

Contendo:

* ID do filme
* Nota Kaggle
* Duração do filme

---

## Arquitetura da Solução

```text
CSV (kaggle_movies.csv)
            |
            |
TMDB API -----> Extract
                    |
                    v
               movies.json
                    |
                    v
                Transform
                    |
                    v
         transformed_movies.json
                    |
                    v
                  Load
                    |
                    v
               PostgreSQL
                    |
                    v
                Consultas
```

---

## Estrutura do Projeto

```text
.
├── dags
│   └── teste-1.py
│
├── etl
│   ├── extract.py
│   ├── transform.py
│   ├── load.py
│   └── validate.py
│
├── sql
│   ├── init.sql
│   └── queries.sql
│
├── data
│   ├── kaggle_movies.csv
│   ├── movies.json
│   └── transformed_movies.json
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Pipeline ETL

### Extract

Responsável por consultar a API TMDB e obter informações de 20 filmes populares e bem avaliados.

Saída:

```text
movies.json
```

### Transform

Realiza o cruzamento dos dados obtidos pela API com os dados presentes no arquivo CSV.

Saída:

```text
transformed_movies.json
```

### Load

Responsável por carregar os dados transformados no PostgreSQL.

Modelo utilizado:

* dim_movie
* dim_release_date
* fact_movie_metrics

### Validate

Executa validações de qualidade de dados antes da utilização das informações.

Validações implementadas:

1. Verificação de existência de registros na tabela fato.
2. Verificação de valores negativos.
3. Verificação de integridade referencial entre fato e dimensões.

---

## Modelo Dimensional

### Dimensão Filme

```text
dim_movie
```

Campos:

* movie_id
* title
* original_language
* status

### Dimensão Data

```text
dim_release_date
```

Campos:

* date_id
* release_date
* release_year
* release_month
* release_day

### Tabela Fato

```text
fact_movie_metrics
```

Campos:

* movie_id
* date_id
* budget
* revenue
* profit
* vote_average
* kaggle_score
* kaggle_runtime

---

## Orquestração com Airflow

DAG:

```text
movies_etl_pipeline
```

Tasks:

1. extract_tmdb_data
2. transform_movie_data
3. load_movie_data
4. validate_loaded_data

Fluxo:

```text
extract
    ↓
transform
    ↓
load
    ↓
validate
```

---

## Consultas de Negócio

As consultas utilizadas no projeto encontram-se em:

```text
sql/queries.sql
```

Consultas implementadas:

1. Top 10 filmes por lucro.
2. Top 10 filmes mais bem avaliados.
3. Top 10 filmes por receita.

---

## Como Executar

### 1. Clonar o repositório

```bash
git clone https://github.com/lucaddonato/data-integration
cd data-integration
```

### 2. Configurar a variável da API

Colocar o arquivo (fiz o upload):

```text
.env
```

### 3. Subir os containers

```bash
docker compose up --build
```

### 4. Acessar o Airflow

```text
http://localhost:8080
```

### 5. Executar a DAG

DAG:

```text
movies_etl_pipeline
```

---

## Tecnologias Utilizadas

* Python 3.10
* Docker
* Docker Compose
* Apache Airflow 2.8
* PostgreSQL 15
* Pandas
* Requests
* Psycopg2

---

## Integrantes

* Luca De Donato Paulillo
