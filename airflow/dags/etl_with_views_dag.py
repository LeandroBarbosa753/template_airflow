from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime
import boto3
import os
import pandas as pd


def pegando_dados_do_banco(**context): # pegar o "contexto de execução da DAG" (como data de execução, task_id, e mais importante: os recursos do XCom).
    hook = PostgresHook(postgres_conn_id="postgres_airflow") # postgres_conn_id – The postgres conn id reference to a specific postgres database. (basicamente instanciar o banco)
    df = hook.get_pandas_df("SELECT * FROM public.connection WHERE 'host' = 'localhost' LIMIT 1;")
    print(f'Resultado: {df}')



with DAG()
   



