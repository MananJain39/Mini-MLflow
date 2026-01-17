from Server.services.tracker import Tracker

_tracker = Tracker()
_active_run = None
_active_experiment = None

def set_experiment(name: str):
    global _active_experiment
    _active_experiment = _tracker.get_or_create_experiment(name)
    return _active_experiment

class start_run:
    def __enter__(self):
        global _active_run
        if _active_experiment is None:
            raise RuntimeError("No active Experiment set")
        
        _active_run = _tracker.start_run(_active_experiment.id)
        return _active_run
    
    def __exit__(self, exc_type, exc, tb):
        _tracker.end_run(_active_run.id)