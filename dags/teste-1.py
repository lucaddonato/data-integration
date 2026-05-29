from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime


with DAG(
    dag_id="movies_etl_pipeline",
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
    catchup=False,
) as dag:

    extract = BashOperator(
        task_id="extract_tmdb_data",
        bash_command="python /opt/airflow/etl/extract.py",
    )

    transform = BashOperator(
        task_id="transform_movie_data",
        bash_command="python /opt/airflow/etl/transform.py",
    )

    load = BashOperator(
        task_id="load_movie_data",
        bash_command="python /opt/airflow/etl/load.py",
    )

    validate = BashOperator(
        task_id="validate_loaded_data",
        bash_command="python /opt/airflow/etl/validate.py",
    )

    extract >> transform >> load >> validate