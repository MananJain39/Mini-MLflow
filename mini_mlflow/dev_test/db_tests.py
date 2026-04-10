from mini_mlflow.server.db.models import Artifact, Experiment, Metric, Param, Run
from mini_mlflow.server.db.session import SessionLocal
from mini_mlflow.server.services.run_service import RunService
from mini_mlflow.server.services.experiment_service import ExperimentService
from mini_mlflow.server.services.logging_service import LoggingService


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

        db.query(Experiment).filter_by(name=experiment_name).delete(
            synchronize_session=False
        )
        db.commit()
    finally:
        db.close()


def test_get_or_create_experiment_returns_same_record_for_same_name():
    tracker = Tracker()
    exp_name = "db_test_exp"
    _cleanup_experiment(exp_name)

    first = tracker.get_or_create_experiment(exp_name)
    second = tracker.get_or_create_experiment(exp_name)

    assert first.id == second.id

    _cleanup_experiment(exp_name)


def test_end_run_updates_status_and_end_time():
    tracker = Tracker()
    exp_name = "db_test_run_end"
    _cleanup_experiment(exp_name)

    exp = tracker.get_or_create_experiment(exp_name)
    run = tracker.start_run(exp.id)

    ended = tracker.end_run(run.id)

    assert ended.status == "FINISHED"
    assert ended.end_time is not None

    db = SessionLocal()
    try:
        db_run = db.get(Run, run.id)
        assert db_run is not None
        assert db_run.status == "FINISHED"
        assert db_run.end_time is not None
    finally:
        db.close()
        _cleanup_experiment(exp_name)
