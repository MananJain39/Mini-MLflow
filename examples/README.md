# Mini-MLflow Tracking Examples

This folder contains two real-world End-To-End Machine Learning examples that demonstrate how to use the `mini_mlflow` client to seamlessly track experiments, hyperparameters, metrics, and models.

These examples are built on the custom models and datasets you provided.

## Prerequisites

If you haven't already, please install the example-specific dependencies:

```bash
pip install -e .[examples]
```

## Running the Examples

Make sure your local Mini-MLflow server is running before executing these scripts!

In a terminal, start the server:
```bash
uvicorn mini_mlflow.server.main:app --reload
```

Then in a separate terminal window, simply execute the example scripts:

### 1. Bangalore Housing Price (Regression)
Predict housing prices using a `RandomForestRegressor` and the `scikit-learn` Pipeline.

```bash
python examples/housing_regression.py
```

**What it does:**
- Authenticates with the local tracker
- Cleans and prepares the CSV dataset
- Trains a `RandomForestRegressor`
- Tracks the `n_estimators`, `max_depth`, and `model_type` parameters
- Tracks `mse` and `r2_score` test metrics
- Uploads the trained pipeline model as `housing_model.pkl` to the backend artifacts store

### 2. Product Sentiment Classification (NLP)
Classifies text sentiment from reviews using `TfidfVectorizer` and `LogisticRegression`.

```bash
python examples/sentiment_classification.py
```

**What it does:**
- Tracks an NLP feature extraction and classification pipeline
- Evaluates evaluation metrics `accuracy` and `f1_score`
- Ships the final `sentiment_pipeline.pkl` to the backend

## E2E Automated Tests

To programmatically test these exact workflows without starting the server manually, you can run our E2E pytest suite from the project root:

```bash
pytest tests/e2e/ -v -s
```
