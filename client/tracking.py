from Server.services.tracker import Tracker

_tracker = Tracker()
_active_run = None
_active_experiment = None

def set_experiment(name: str):
    global _active_experiment
    _active_experiment = _tracker.get_or_create_experiment(name)
    return _active_experiment