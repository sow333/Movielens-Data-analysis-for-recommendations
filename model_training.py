def train_model():
    conn = sqlite3.connect('/tmp/movielens.db')
    movie_ratings = pd.read_sql('SELECT * FROM movie_ratings', conn)
    
    reader = Reader(rating_scale=(0.5, 5.0))
    data = Dataset.load_from_df(movie_ratings[['userId', 'movieId', 'rating']], reader)
    
    trainset, testset = train_test_split(data, test_size=0.25)
    
    model = SVD()
    model.fit(trainset)
    
    predictions = model.test(testset)
    
    # Store model predictions
    with open('/tmp/predictions.txt', 'w') as f:
        for pred in predictions:
            f.write(f"{pred.uid}\t{pred.iid}\t{pred.est}\n")

train_task = PythonOperator(
    task_id='train_model',
    python_callable=train_model,
    dag=dag,
)

