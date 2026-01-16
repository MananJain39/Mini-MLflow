from Server.services.tracker import Tracker

t = Tracker()
e1 = t.get_or_create_experiment("exp1")
# e2 = t.get_or_create_experiment("exp2")
run = t.start_run(e1.id)

print(run.id, run.status)  

t.log_param(run.id, "lr", 1)
t.log_param(run.id, "batch_size", 32)

print("Param Logged")

t.log_metric(run.id, "mt", 1.234, step = 1)
t.log_metric(run.id, "mt2", 1.2356, step = 1)

print("Metric working")

