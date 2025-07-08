# Projeto de ETL com Apache Airflow

Este projeto é uma exploração prática do **Apache Airflow** aplicado a tarefas de **ETL (Extract, Transform, Load)**. Ele utiliza diferentes operadores para manipulação e orquestração de dados, além de integração com serviços como **MinIO**, **PostgreSQL**, **MariaDB** e **Metabase** para visualização de dados.

> ⚠️ Este repositório é baseado em um fork, mas sofreu modificações significativas com foco em aprendizado, testes e integração com múltiplos serviços.

---

## 🚀 Objetivo

Demonstrar o uso de operadores do Airflow para construir pipelines ETL, com apoio de um ambiente Docker para orquestração dos serviços envolvidos.

---

## 🗂️ Estrutura do Projeto

```
├── acesso_interface__airflow.txt
├── airflow
│   ├── config_airflow
│   │   └── airflow.Dockerfile
│   └── dags
│       ├── etl_with_views_dag.py         # DAG principal para processo ETL com views
│       └── operator_test.py              # DAG auxiliar para testes com operadores
├── docker-compose.yml                    # Orquestração completa dos serviços
├── requirements.txt                      # Dependências Python para o Airflow
```

---

## 🐳 Serviços via Docker Compose

- **Airflow** (com LocalExecutor)
- **PostgreSQL** (para Airflow)
- **MariaDB** (banco de dados de origem)
- **MinIO** (armazenamento de dados simulando S3)
- **Metabase** (ferramenta de BI para visualização)
- **PostgreSQL Metabase** (banco interno do Metabase)

---

## ⚙️ Como executar

1. Clone o projeto:
   ```bash
   git clone <url-do-seu-repo>
   cd <nome-do-projeto>
   ```

2. Suba os serviços com Docker Compose:
   ```bash
   docker-compose up --build
   ```

3. Acesse as interfaces:
   - Airflow: [http://localhost:8080](http://localhost:8080)
   - MinIO: [http://localhost:9001](http://localhost:9001) (login: `minioadmin` / `minio@1234!`)
   - Metabase: [http://localhost:3000](http://localhost:3000)

---

## 📊 Casos de Uso

- Criar pipelines com múltiplos operadores (PythonOperator, BashOperator, etc).
- Utilizar banco de dados relacional (MariaDB) como origem de dados.
- Salvar dados transformados em bucket MinIO (simulando S3).
- Visualizar os dados processados via Metabase.

---

## 📌 Observações

- O DAG `etl_with_views_dag.py` é o principal fluxo de ETL.
- Os arquivos `.txt` como `acesso_interface__airflow.txt` servem como dados de entrada ou documentação complementar.
- O projeto está em constante evolução para testes e estudo do Airflow em ambientes reais.

---

## 🛠️ Tecnologias Utilizadas

- [Apache Airflow](https://airflow.apache.org/)
- [Docker + Docker Compose](https://docs.docker.com/)
- [MinIO](https://min.io/)
- [MariaDB](https://mariadb.org/)
- [PostgreSQL](https://www.postgresql.org/)
- [Metabase](https://www.metabase.com/)

---

## 📄 Licença

Este projeto é livre para fins educacionais e pode ser modificado conforme necessário.

---

## ✨ Créditos

Este projeto foi originalmente baseado em um fork de outro repositório com propósitos semelhantes, mas passou por modificações estruturais e de conteúdo.
