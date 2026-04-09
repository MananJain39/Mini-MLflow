import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import pickle
import os

from mini_mlflow.client.tracking import MiniMLflowClient

def convert_sqft(val):
    try:
        if "-" in val:  
            token = val.split("-")  
            return (float(token[0]) + float(token[1])) / 2 
        return float(val) 
    except:
        return None

def preprocess_data(df):
    df = df.drop(['\\area_type', "availability", "society", 'balcony'], axis=1)
    df = df.dropna()
    df["size"] = df["size"].str.extract(r'(\d+)').astype(int)
    df.rename(columns={'size': 'bhk'}, inplace=True)
    df['total_sqft'] = df['total_sqft'].apply(convert_sqft)
    df = df.dropna(subset=['total_sqft'])
    df = df.reset_index(drop=True)
    df = df[(df["bhk"] <= 10) & (df["price"] <= 500)]
    return df

def train():
    file_path = "C:\\Code Files\\Project\\Bangalore_Housing_Price\\BHP.csv"
    if not os.path.exists(file_path):
        print(f"Dataset not found at expected path: {file_path}")
        return

    print("Loading data...")
    df = pd.read_csv(file_path)
    df = preprocess_data(df)

    X = df.drop("price", axis=1)
    y = df["price"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore'), ['location'])
        ],
        remainder='passthrough'
    )

    n_estimators = 50
    max_depth = 10

    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('model', RandomForestRegressor(n_estimators=n_estimators, max_depth=max_depth, random_state=42))
    ])

    client = MiniMLflowClient(base_url="http://localhost:8000/api")
    client.set_experiment("Bangalore_Housing")

    print("Starting training run...")
    with client.run() as run:
        client.log_param("n_estimators", str(n_estimators))
        client.log_param("max_depth", str(max_depth))
        client.log_param("model_type", "RandomForestRegressor")
        client.log_tag("dataset", "BHP")

        pipeline.fit(X_train, y_train)

        y_pred = pipeline.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        client.log_metric("mse", mse)
        client.log_metric("r2_score", r2)

        # Save model
        model_filename = "housing_model.pkl"
        with open(model_filename, "wb") as f:
            pickle.dump(pipeline, f)
        
        client.log_artifact(model_filename)
        os.remove(model_filename)

    print(f"Training Complete. MSE: {mse:.4f}, R2: {r2:.4f}")

if __name__ == "__main__":
    train()
