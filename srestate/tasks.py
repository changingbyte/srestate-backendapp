from venv import create
from celery import task 
from celery import shared_task 
# We can have either registered task 
from property.models import InCharge
import datetime
from chat.tasks import send_import_summary
@task(name='summary') 
def send_import_summary():
    print("summary")
    return send_import_summary


# or 
@shared_task 
def send_notifiction():
     print("here i am")
     # Another trick