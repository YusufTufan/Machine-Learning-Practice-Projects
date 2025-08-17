from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id="example_dag",
    start_date=datetime(2025, 8, 15),
    schedule_interval=None,
    catchup=False,
) as dag:

    task1 = BashOperator(
        task_id="print_hello",
        bash_command='echo "Hello from Airflow!"'
    )

    task2 = BashOperator(
        task_id="print_date",
        bash_command="date"
    )

    task1 >> task2
