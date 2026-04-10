# Mini-MLflow Quickstart Guide

Here is the step-by-step process to run your project end-to-end and verify that everything is working.

## 1. Running the Automated Tests
The best way to verify the project is working is to run the comprehensive test suite locally. The project uses `pytest`.

```bash
# Run all tests (unit, integration)
python -m pytest

# Or to see test coverage
python -m pytest --cov=mini_mlflow --cov-report=term-missing
```

*Note: All 26 tests are currently passing successfully!*

## 2. Starting the Backend Server
The server is built with FastAPI. You can start it using `uvicorn`. This must be running before the client can log data to it.

```bash
# Start the server with hot-reload enabled
python -m uvicorn mini_mlflow.server.main:app --reload --host 127.0.0.1 --port 8000
```
*The server will be available at `http://127.0.0.1:8000`. You can visit `http://127.0.0.1:8000/docs` to see the interactive Swagger API documentation.*

## 3. Using the Client (End-to-End Workflow)
Once the server is running, you can use the Python tracking client to log experiments. 

Here is an example script you can run (e.g., save as `test_run.py` and run `python test_run.py`):

```python
from mini_mlflow.client.tracking import Tracker

# 1. Initialize Tracker pointing to your local server
tracker = Tracker(server_uri="http://127.0.0.1:8000")

# 2. Create or Get an Experiment
exp = tracker.create_experiment(name="My First Experiment")
print(f"Experiment Created: {exp.experiment_id}")

# 3. Start a tracking run
run = tracker.start_run(
    experiment_id=exp.experiment_id,
    run_name="Baseline Model"
)

# 4. Log parameters and metrics
tracker.log_param(run.run_id, "learning_rate", 0.01)
tracker.log_metric(run.run_id, "accuracy", 0.95)

# 5. End the run
tracker.end_run(run.run_id)
print("Run completed successfully!")
```

## 4. End-to-End Test Options
For a fully working end-to-end regression workflow that is already included in your project, you can run:
```bash
python examples/housing_regression.py
```
*(Make sure the server is running in another terminal before executing the example).*
