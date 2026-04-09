import pytest
from unittest.mock import patch
import sys
import os

# Add project root to sys path so examples can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from examples.housing_regression import train

def test_housing_workflow_e2e(api_client, capsys):
    """
    Test the housing regression script end-to-end.
    We patch the tracking client's internal requests to use the FastAPI TestClient
    so we don't need a live server running.
    """
    def mock_request(self_session, method, url, **kwargs):
        # Route request to the FastAPI test client
        path = url.replace("http://localhost:8000", "")
        # Remove requests-specific kwargs that httpx TestClient doesn't accept
        kwargs.pop("timeout", None)
        resp = api_client.request(method, path, **kwargs)
        if not hasattr(resp, "ok"):
            resp.ok = resp.is_success
        return resp

    with patch("mini_mlflow.client.tracking._req.Session.request", new=mock_request):
        # Run the actual example script
        train()

    # We capture standard output to verify the example printed success
    captured = capsys.readouterr()
    assert "Training Complete" in captured.out

    # Now verify the backend database state via the API!
    resp = api_client.get("/api/experiments")
    assert resp.status_code == 200
    experiments = resp.json()
    
    assert any(e["name"] == "Bangalore_Housing" for e in experiments), "Experiment not created."
    
    # Get that experiment id
    exp_id = next(e["id"] for e in experiments if e["name"] == "Bangalore_Housing")
    
    # List runs
    runs_resp = api_client.get(f"/api/experiments/{exp_id}/runs")
    assert runs_resp.status_code == 200
    runs = runs_resp.json()
    assert len(runs) >= 1, "No runs recorded for the experiment."
    
    run_id = runs[0]["run_id"] if "run_id" in runs[0] else runs[0]["id"]
    
    # Check if params, metrics, and tags were logged
    details = api_client.get(f"/api/runs/{run_id}").json()
    
    params = {p["key"]: p["value"] for p in details.get("params", [])}
    assert "n_estimators" in params
    assert "model_type" in params
    
    metrics = {m["key"]: m["value"] for m in details.get("metrics", [])}
    assert "mse" in metrics
    assert "r2_score" in metrics

    tags = {t["key"]: t["value"] for t in details.get("tags", [])}
    assert "dataset" in tags
    assert tags["dataset"] == "BHP"
    
    artifacts = [a["path"] for a in details.get("artifacts", [])]
    assert any("housing_model.pkl" in a for a in artifacts)
