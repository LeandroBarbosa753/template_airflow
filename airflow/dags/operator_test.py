# 1. Importações Essenciais
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime
import boto3
import os
import pandas as pd

# 2. Definindo a Função Python para a Primeira Tarefa
def pegando_dados_do_banco(**context): #pegar o "contexto de execução da DAG" (como data de execução, task_id, e mais importante: os recursos do XCom).
    ''' 
    Esta função se conecta ao PostgreSQL, executa uma query,
    salva o resultado em um arquivo Parquet e o compartilha via XCom.
    '''
    print("Iniciando a busca de dados no banco...")
    # Usando o Hook para se conectar ao banco definido na UI do Airflow
    hook = PostgresHook(postgres_conn_id="postgres_airflow")
    df = hook.get_pandas_df("SELECT * FROM public.connection WHERE host = 'localhost';")
    print('A busca de dados e criação do DF deu certo.')
    print(f' o resultado é: {df}')

    # Define um caminho temporário para o arquivo
    file_path = "/tmp/resultado.parquet"    
    df.to_parquet(file_path, index=False)
    print(f"Arquivo Parquet salvo em: {file_path}")

    # Empurrando o caminho do arquivo para o XCom (Cross-Communication) para que outras tarefas possam usá-lo
    context['ti'].xcom_push(key='parquet_path', value=file_path)
    '''
    **context: É um dicionário que o Airflow passa para a sua função Python. 
    Ele contém informações valiosas sobre a execução, como a task_instance (ti),
     que é o objeto que usamos para acessar o XCom (ti.xcom_push e ti.xcom_pull).
    '''

# 3. Definindo a Função Python para a Segunda Tarefa
def upload_parquet_to_minio(**context):
    '''
    Esta função recupera o caminho do arquivo do XCom e faz o upload para o MinIO.
    '''
    print("Iniciando upload para o MinIO...")

    # Puxando o valor do XCom da tarefa 'fazer_busca'
    file_path = context['ti'].xcom_pull(
        key='parquet_path',
        task_ids='processamento_dados.fazer_busca'  # ID completo: 'task_group_id.task_id'
    )

    if not file_path:
        raise ValueError("Caminho do arquivo não encontrado no XCom. A tarefa anterior falhou?")
    
    # Configurações do cliente MinIO (S3)
    # As credenciais são pegas das variáveis de ambiente definidas no docker-compose.yml
    minio_endpoint = os.environ.get('MINIO_ENDPOINT','http://localhost:9000')
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
    print(f"✅ Arquivo enviado com sucesso para o MinIO: s3://{bucket_name}/{object_name}")


with DAG(

    dag_id= "operator_test",  # Nome único da sua DAG
    start_date=datetime(2024, 1, 1), # Data de início a partir da qual a DAG pode ser agendada
    schedule_interval=None, # Define a frequência. `None` significa que só será executada manualmente. 
    catchup=False  # `False` impede que a DAG execute agendamentos passados que foram perdidos.
    ) as dag:

    # 5. Definição das Tarefas (instâncias dos Operadores)    
    usando_bash = BashOperator(
        task_id="usando_bash", 
        bash_command="echo 'Essa é a DAG de exemplo, aqui estão meus testes para aprendizado'"
    )
    # 6. Usando um TaskGroup para organizar tarefas relacionadas visualmente
    with TaskGroup("processamento_dados") as processamento:
        fazer_busca = PythonOperator(
            task_id="fazer_busca",
            python_callable=pegando_dados_do_banco,
            provide_context=True
        )

        upload_task = PythonOperator(
            task_id="upload_parquet_to_minio",
            python_callable=upload_parquet_to_minio,
            #provide_context=True foi depreciado. O contexto é passado por padrão.()
        )

        # select_task = PostgresOperator(
        #     task_id="select_coluna",
        #     postgres_conn_id="postgres_airflow",
        #     sql="SELECT * FROM public.connection WHERE host = 'localhost';"
        # )

        # Definindo a dependência DENTRO do TaskGroup
        fazer_busca >> upload_task

# 7. Definindo a ordem de execução geral (dependências)
    usando_bash >> processamento

   

