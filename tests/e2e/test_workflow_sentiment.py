import pytest
from unittest.mock import patch
import sys
import os

# Add project root to sys path so examples can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from examples.sentiment_classification import train

def test_sentiment_workflow_e2e(api_client, capsys):
    """
    Test the sentiment classification script end-to-end.
    """
    def mock_request(self_session, method, url, **kwargs):
        # Route request to the FastAPI test client
        path = url.replace("http://localhost:8000", "")
        kwargs.pop("timeout", None)
        resp = api_client.request(method, path, **kwargs)
        if not hasattr(resp, "ok"):
            resp.ok = resp.is_success
        return resp

    with patch("mini_mlflow.client.tracking._req.Session.request", new=mock_request):
        # Run the actual example script
        train()

    # Verify script output
    captured = capsys.readouterr()
    assert "Training Complete" in captured.out

    # Now verify the backend database state via the API!
    experiments = api_client.get("/api/experiments").json()
    assert any(e["name"] == "Product_Review_Sentiment" for e in experiments), "Experiment not created."
    
    # Get that experiment id
    exp_id = next(e["id"] for e in experiments if e["name"] == "Product_Review_Sentiment")
    
    # List runs
    runs = api_client.get(f"/api/experiments/{exp_id}/runs").json()
    assert len(runs) >= 1, "No runs recorded for the experiment."
    
    run_id = runs[0]["run_id"] if "run_id" in runs[0] else runs[0]["id"]
    
    # Check if params, metrics, and tags were logged
    details = api_client.get(f"/api/runs/{run_id}").json()
    
    params = {p["key"]: p["value"] for p in details.get("params", [])}
    assert "max_features" in params
    assert "model_type" in params
    assert params["model_type"] == "LogisticRegression"
    
    metrics = {m["key"]: m["value"] for m in details.get("metrics", [])}
    assert "accuracy" in metrics
    assert "f1_score" in metrics

    tags = {t["key"]: t["value"] for t in details.get("tags", [])}
    assert tags.get("dataset") == "balanced_sentiment"
    
    artifacts = [a["path"] for a in details.get("artifacts", [])]
    assert any("sentiment_pipeline.pkl" in a for a in artifacts)
