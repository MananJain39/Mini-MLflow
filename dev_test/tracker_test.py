from Server.services.tracker import Tracker

t = Tracker()
e1 = t.get_or_create_experiment("exp1")
# e2 = t.get_or_create_experiment("exp2")
run = t.start_run(e1.id)


print(run.id, run.status)  
