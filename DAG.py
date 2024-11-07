from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
import pandas as pd
import sqlite3
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split

default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
}

dag = DAG(
    'movielens_pipeline',
    default_args=default_args,
    description='A pipeline for Movielens movie recommendations',
    schedule_interval='@daily',
)

# 1. Task: Data Ingestion
def ingest_data():
    movies = pd.read_csv('http://files.grouplens.org/datasets/movielens/ml-latest-small/movies.csv')
    ratings = pd.read_csv('http://files.grouplens.org/datasets/movielens/ml-latest-small/ratings.csv')
    movies.to_csv('/tmp/movies.csv', index=False)
    ratings.to_csv('/tmp/ratings.csv', index=False)

ingest_task = PythonOperator(
    task_id='ingest_data',
    python_callable=ingest_data,
    dag=dag,
)

# 2. Task: Data Cleaning and Storage
def clean_and_store():
    movies = pd.read_csv('/tmp/movies.csv')
    ratings = pd.read_csv('/tmp/ratings.csv')

    movie_ratings = pd.merge(ratings, movies, on='movieId')

    # Create SQLite connection
    conn = sqlite3.connect('/tmp/movielens.db')
    
    # Store cleaned data into SQLite
    movie_ratings.to_sql('movie_ratings', conn, if_exists='replace', index=False)

clean_task = PythonOperator(
    task_id='clean_and_store_data',
    python_callable=clean_and_store,
    dag=dag,
)

