from airflow import DAG
from airflow.operators.bash import BashOperator
#from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.python import PythonOperator
from datetime import datetime
import boto3
import os
import pandas as pd


def pegando_dados_do_banco(**context): #pegar o "contexto de execução da DAG" (como data de execução, task_id, e mais importante: os recursos do XCom).
    hook = PostgresHook(postgres_conn_id="postgres_airflow")
    df = hook.get_pandas_df("SELECT * FROM public.connection WHERE host = 'localhost';")
    print('A busca de dados e criação do DF deu certo.')
    print(f' o resultado é: {df}')


    file_path = "/tmp/resultado.parquet"    
    df.to_parquet(file_path, index=False)

    context['ti'].xcom_push(key='parquet_path', value=file_path)

def upload_parquet_to_minio(**context):
    # Recupera o caminho salvo no XCom
    file_path = context['ti'].xcom_pull(
        key='parquet_path',
        task_ids='select_and_print'
    )

    minio_endpoint = os.environ['MINIO_ENDPOINT']
    access_key = os.environ['MINIO_ACCESS_KEY']
    secret_key = os.environ['MINIO_SECRET_KEY']
    bucket_name = 'bucket-de-dados-da-atividade'
    object_name = 'resultado.parquet'

    s3 = boto3.client(
        's3',
        endpoint_url=minio_endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key
    )

    s3.upload_file(file_path, bucket_name, object_name)
    print(f"✅ Arquivo enviado ao MinIO: s3://{bucket_name}/{object_name}")


with DAG(

    dag_id= "operator_test", 
    start_date=datetime(2024, 1, 1), 
    schedule=None, 
    catchup=False
    ) as dag:
        
    usando_bash = BashOperator(
        task_id="usando_bash", 
        bash_command="echo 'Essa é a DAG de exemplo, aqui estão meus testes para aprendizado'"
    )
    fazer_busca=PythonOperator(
        task_id="fazer_busca",
        python_callable=pegando_dados_do_banco,
        provide_context=True
    )

    """select_task= PostgresOperator
    (
      task_id="select_coluna",
      postgres_conn_id="postgres_airflow",
      sql="SELECT * FROM public.connection WHERE host = 'localhost';"
    )"""

    upload_task = PythonOperator(
        task_id="upload_parquet_to_minio",
        python_callable=upload_parquet_to_minio,
        provide_context=True
    )


    # Ordem de execução das tarefas
    usando_bash >> fazer_busca >> upload_task
    

