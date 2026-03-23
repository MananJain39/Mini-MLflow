"""Unit tests for the Tracker service layer."""

from pathlib import Path

import pytest
from Server.services.tracker import Tracker
from Server.DB.models import Experiment, Run, Param, Metric, Artifact


@pytest.fixture()
def tracker():
    return Tracker()


# ── Experiments ──────────────────────────────────────────────────────

class TestGetOrCreateExperiment:
    def test_creates_new_experiment(self, tracker, db):
        exp = tracker.get_or_create_experiment("exp-new")
        assert exp.name == "exp-new"
        assert exp.id is not None
        assert db.query(Experiment).count() == 1

    def test_returns_existing_for_same_name(self, tracker):
        first = tracker.get_or_create_experiment("dup")
        second = tracker.get_or_create_experiment("dup")
        assert first.id == second.id


# ── Runs ─────────────────────────────────────────────────────────────

class TestStartRun:
    def test_creates_run_with_running_status(self, tracker, db):
        exp = tracker.get_or_create_experiment("run-exp")
        run = tracker.start_run(exp.id)
        assert run.status == "RUNNING"
        assert run.start_time is not None
        assert db.query(Run).count() == 1


class TestEndRun:
    def test_marks_run_finished(self, tracker):
        exp = tracker.get_or_create_experiment("end-exp")
        run = tracker.start_run(exp.id)
        ended = tracker.end_run(run.id)
        assert ended.status == "FINISHED"
        assert ended.end_time is not None

    def test_raises_for_unknown_run(self, tracker):
        with pytest.raises(ValueError, match="Run not found"):
            tracker.end_run("nonexistent-id")


# ── Params ───────────────────────────────────────────────────────────

class TestLogParam:
    def test_stores_param(self, tracker, db):
        exp = tracker.get_or_create_experiment("param-exp")
        run = tracker.start_run(exp.id)
        param = tracker.log_param(run.id, "lr", "0.01")
        assert param.key == "lr"
        assert param.value == "0.01"
        assert db.query(Param).filter_by(run_id=run.id).count() == 1

    def test_raises_for_unknown_run(self, tracker):
        with pytest.raises(ValueError, match="Run not found"):
            tracker.log_param("bad-id", "k", "v")


# ── Metrics ──────────────────────────────────────────────────────────

class TestLogMetric:
    def test_stores_metric(self, tracker, db):
        exp = tracker.get_or_create_experiment("metric-exp")
        run = tracker.start_run(exp.id)
        metric = tracker.log_metric(run.id, "mae", 1.23, step=1)
        assert metric.key == "mae"
        assert metric.value == pytest.approx(1.23)
        assert metric.step == 1
        assert db.query(Metric).filter_by(run_id=run.id).count() == 1

    def test_raises_for_unknown_run(self, tracker):
        with pytest.raises(ValueError, match="Run not found"):
            tracker.log_metric("bad-id", "k", 0.5)


# ── Artifacts ────────────────────────────────────────────────────────

class TestLogArtifact:
    def test_copies_file_and_stores_record(self, tracker, db, tmp_path):
        exp = tracker.get_or_create_experiment("art-exp")
        run = tracker.start_run(exp.id)

        src = tmp_path / "data.csv"
        src.write_text("a,b\n1,2\n", encoding="utf-8")

        artifact = tracker.log_artifact(run.id, str(src))
        assert Path(artifact.path).exists()
        assert db.query(Artifact).filter_by(run_id=run.id).count() == 1

    def test_raises_for_missing_file(self, tracker):
        exp = tracker.get_or_create_experiment("art-exp2")
        run = tracker.start_run(exp.id)
        with pytest.raises(ValueError, match="File not found"):
            tracker.log_artifact(run.id, "/nonexistent/file.txt")

    def test_raises_for_unknown_run(self, tracker):
        with pytest.raises(ValueError, match="Run not found"):
            tracker.log_artifact("bad-id", "some/path")
