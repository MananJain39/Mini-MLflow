"""Unit tests for the new Services layer (Experiment, Run, Logging)."""

from pathlib import Path
import pytest
from mini_mlflow.server.services.experiment_service import ExperimentService
from mini_mlflow.server.services.run_service import RunService
from mini_mlflow.server.services.logging_service import LoggingService
from mini_mlflow.server.db.models import Experiment, Run, Param, Metric, Artifact


@pytest.fixture()
def experiment_service():
    return ExperimentService()

@pytest.fixture()
def run_service():
    return RunService()

@pytest.fixture()
def logging_service():
    return LoggingService()

# ── Experiments ──────────────────────────────────────────────────────

class TestExperimentService:
    def test_creates_new_experiment(self, experiment_service, db):
        exp = experiment_service.get_or_create_experiment("exp-new")
        assert exp.name == "exp-new"
        assert exp.id is not None
        assert db.query(Experiment).count() == 1

    def test_returns_existing_for_same_name(self, experiment_service):
        first = experiment_service.get_or_create_experiment("dup")
        second = experiment_service.get_or_create_experiment("dup")
        assert first.id == second.id

# ── Runs ─────────────────────────────────────────────────────────────

class TestRunService:
    def test_creates_run_with_running_status(self, experiment_service, run_service, db):
        exp = experiment_service.get_or_create_experiment("run-exp")
        run = run_service.start_run(exp.id)
        assert run.status == "RUNNING"
        assert run.start_time is not None
        assert db.query(Run).count() == 1

    def test_marks_run_finished(self, experiment_service, run_service):
        exp = experiment_service.get_or_create_experiment("end-exp")
        run = run_service.start_run(exp.id)
        ended = run_service.end_run(run.id)
        assert ended.status == "FINISHED"
        assert ended.end_time is not None

    def test_raises_for_unknown_run(self, run_service):
        with pytest.raises(ValueError, match="Run not found"):
            run_service.end_run("nonexistent-id")

# ── Logging ──────────────────────────────────────────────────────────

class TestLoggingService:
    def test_stores_param(self, experiment_service, run_service, logging_service, db):
        exp = experiment_service.get_or_create_experiment("param-exp")
        run = run_service.start_run(exp.id)
        param = logging_service.log_param(run.id, "lr", "0.01")
        assert param.key == "lr"
        assert param.value == "0.01"
        assert db.query(Param).filter_by(run_id=run.id).count() == 1

    def test_stores_metric(self, experiment_service, run_service, logging_service, db):
        exp = experiment_service.get_or_create_experiment("metric-exp")
        run = run_service.start_run(exp.id)
        metric = logging_service.log_metric(run.id, "mae", 1.23, step=1)
        assert metric.key == "mae"
        assert metric.value == pytest.approx(1.23)
        assert metric.step == 1
        assert db.query(Metric).filter_by(run_id=run.id).count() == 1

    def test_copies_file_and_stores_record(self, experiment_service, run_service, logging_service, db, tmp_path):
        exp = experiment_service.get_or_create_experiment("art-exp")
        run = run_service.start_run(exp.id)

        src = tmp_path / "data.csv"
        src.write_text("a,b\n1,2\n", encoding="utf-8")

        artifact = logging_service.log_artifact(run.id, str(src))
        assert Path(artifact.path).exists()
        assert db.query(Artifact).filter_by(run_id=run.id).count() == 1

    def test_raises_for_missing_file(self, experiment_service, run_service, logging_service):
        exp = experiment_service.get_or_create_experiment("art-exp2")
        run = run_service.start_run(exp.id)
        with pytest.raises(ValueError, match="File not found"):
            logging_service.log_artifact(run.id, "/nonexistent/file.txt")
