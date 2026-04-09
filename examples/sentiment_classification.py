import pandas as pd
import numpy as np
import re
import nltk
from nltk.stem import WordNetLemmatizer
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, f1_score
import pickle
import os

from mini_mlflow.client.tracking import MiniMLflowClient

nltk.download('wordnet', quiet=True)
lemmatizer = WordNetLemmatizer()

def _clean_text(text):
    text = text.lower()
    text = text.replace("'", " ")
    text = text.replace('"', " ")
    text = text.replace("`", " ")
    text = text.replace("!", " ")
    text = text.replace("?", " ")
    text = text.replace(",", " ")
    text = text.replace(".", " ")
    return text

def advanced_clean(text):
    text = _clean_text(str(text))
    text = re.sub(r"[^a-zA-Z\s]", " ", text)
    words = text.split()
    words = [lemmatizer.lemmatize(word) for word in words]
    return " ".join(words)

def train():
    file_path = "C:\\Code Files\\Project\\Product-Review-Sentiment-Analyser\\balanced_sentiment_dataset.csv"
    if not os.path.exists(file_path):
        print(f"Dataset not found at expected path: {file_path}")
        return

    print("Loading data...")
    df = pd.read_csv(file_path, encoding="utf-8")
    
    # We sample the dataset for the example to ensure fast execution during testing
    if len(df) > 5000:
        df = df.sample(5000, random_state=42)

    df.rename(columns={"sentiment": "label", "text": "review"}, inplace=True)
    df.dropna(inplace=True)
    
    print("Preprocessing text...")
    df["clean_review"] = df["review"].apply(advanced_clean)

    X = df["clean_review"]
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    pipeline = Pipeline(steps=[
        ('tfidf', TfidfVectorizer(max_features=5000)),
        ('model', LogisticRegression(max_iter=1000))
    ])

    client = MiniMLflowClient(base_url="http://localhost:8000/api")
    client.set_experiment("Product_Review_Sentiment")

    print("Starting training run...")
    with client.run() as run:
        client.log_param("max_features", "5000")
        client.log_param("model_type", "LogisticRegression")
        client.log_tag("dataset", "balanced_sentiment")

        pipeline.fit(X_train, y_train)

        y_pred = pipeline.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average='weighted')

        client.log_metric("accuracy", float(acc))
        client.log_metric("f1_score", float(f1))

        # Save model
        model_filename = "sentiment_pipeline.pkl"
        with open(model_filename, "wb") as f:
            pickle.dump(pipeline, f)
        
        client.log_artifact(model_filename)
        os.remove(model_filename)

    print(f"Training Complete. Accuracy: {acc:.4f}, F1: {f1:.4f}")

if __name__ == "__main__":
    train()
