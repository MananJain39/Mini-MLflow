from Server.services.tracker import Tracker

t = Tracker()
e1 = t.get_or_create_experiment("exp1")
e2 = t.get_or_create_experiment("exp2")

print(e1.id == e2.id)  # Should be False
