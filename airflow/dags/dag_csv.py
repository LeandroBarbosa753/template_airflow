"""
from datetime import datetime, timedelta
from airflow.decorators import dag, task
from airflow.operators.python import PythonOperator
from airflow.providres.postgres.hooks.postgres import PostgresHook
import boto3
import pandas as pd


##argumens
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 5, 14),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=1),
}

@dag(
    dag_id='postgres_to_minio_csv',
    default_args=default_args,
    description='Carga incremental do postgres no csv-minio',
    schedule_interval=timedelta(days=1),
    catchup=False
)

def postgres_to_minio_etl():
    table_names = ['veiculos', 'estados', 'cidades', 'concessionarias', 'vendedores', 'clientes', 'vendas']

    s3_client = boto3.client(
        's3',
        endpoint_url='http://minio:9000',
        aws_access_key_id='minioadmin',
        aws_secret_access_key='minio@1234!'
    )
    bucket_name = 'landing'

    for table_name in table_names:
        @task(task_id=f'get_max_id{table_name}')
        def get_max_primary_key(table_name:str):
            try:
                response = s3_client.get_object(Bucket = bucket_name, Key = f"") 
        
        
        
        
        # Conectar ao banco de dados PostgreSQL
        pg_hook = PostgresHook(postgres_conn_id='postgres_default')
        conn = pg_hook.get_conn()
        cursor = conn.cursor()

        # Executar a consulta SQL para obter os dados da tabela
        query = f"SELECT * FROM {table_name}"
        cursor.execute(query)
        data = cursor.fetchall()

        # Obter os nomes das colunas
        colnames = [desc[0] for desc in cursor.description]

        # Criar um DataFrame do Pandas com os dados
        df = pd.DataFrame(data, columns=colnames)

        # Salvar o DataFrame como CSV em um buffer
        csv_buffer = df.to_csv(index=False)

        # Enviar o CSV para o MinIO
        s3_client.put_object(
            Bucket=bucket_name,
            Key=f'{table_name}.csv',
            Body=csv_buffer
        )
        print(f"Dados da tabela {table_name} enviados para o MinIO com sucesso.")
        """