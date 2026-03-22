from Server.DB.models import Artifact, Experiment, Metric, Param, Run
from Server.DB.session import SessionLocal
from client.tracking import set_experiment, start_run


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


def test_start_run_context_manager_ends_run():
    exp_name = "client_test_exp"
    _cleanup_experiment(exp_name)

    exp = set_experiment(exp_name)

    with start_run() as run:
        assert run.experiment_id == exp.id
        assert run.status == "RUNNING"

    db = SessionLocal()
    try:
        db_run = db.get(Run, run.id)
        assert db_run is not None
        assert db_run.status == "FINISHED"
        assert db_run.end_time is not None
    finally:
        db.close()
        _cleanup_experiment(exp_name)
