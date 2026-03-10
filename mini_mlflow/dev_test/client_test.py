from client.tracking import set_experiment, start_run
from Server.DB.session import SessionLocal
from Server.DB.models import Run

exp = set_experiment("client_exp1")

with start_run() as run:
    print("Run Started: ", run.id)

db = SessionLocal()
db_run = db.query(Run).get(run.id)

print("Status:", db_run.status)
print("Start:", db_run.start_time)
print("End:", db_run.end_time)
print("Run status after exit:", db_run.status)


db.close()
