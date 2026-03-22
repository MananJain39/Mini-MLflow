from pathlib import Path

from Server.DB.models import Artifact, Experiment, Metric, Param, Run
from Server.DB.session import SessionLocal
from Server.services.tracker import Tracker


def _cleanup_experiment(experiment_name: str):
    db = SessionLocal()
    try:
        run_ids = {
            run.id
            for run in db.query(Run)
            .join(Run.experiment)
            .filter_by(name=experiment_name)
            .all()
        }

        if run_ids:
            db.query(Artifact).filter(Artifact.run_id.in_(run_ids)).delete(
                synchronize_session=False
            )
            db.query(Metric).filter(Metric.run_id.in_(run_ids)).delete(
                synchronize_session=False
            )
            db.query(Param).filter(Param.run_id.in_(run_ids)).delete(
                synchronize_session=False
            )
            db.query(Run).filter(Run.id.in_(run_ids)).delete(synchronize_session=False)

        db.query(Experiment).filter_by(name=experiment_name).delete(synchronize_session=False)
        db.commit()
    finally:
        db.close()


def test_tracker_logs_full_run(tmp_path):
    tracker = Tracker()
    exp_name = "tracker_test_exp"
    artifact_file = tmp_path / "artifact.txt"
    artifact_file.write_text("artifact-content", encoding="utf-8")

    _cleanup_experiment(exp_name)

    exp = tracker.get_or_create_experiment(exp_name)
    run = tracker.start_run(exp.id)

    tracker.log_param(run.id, "lr", 0.1)
    tracker.log_metric(run.id, "mae", 1.23, step=1)
    artifact = tracker.log_artifact(run.id, str(artifact_file))
    ended = tracker.end_run(run.id)

    db = SessionLocal()
    try:
        db_run = db.get(Run, run.id)
        params = db.query(Param).filter_by(run_id=run.id).all()
        metrics = db.query(Metric).filter_by(run_id=run.id).all()
        artifacts = db.query(Artifact).filter_by(run_id=run.id).all()

        assert db_run is not None
        assert ended.status == "FINISHED"
        assert db_run.status == "FINISHED"
        assert len(params) == 1
        assert params[0].key == "lr"
        assert params[0].value == "0.1"
        assert len(metrics) == 1
        assert metrics[0].key == "mae"
        assert metrics[0].step == 1
        assert len(artifacts) == 1
        assert Path(artifact.path).exists()
    finally:
        db.close()
        _cleanup_experiment(exp_name)
