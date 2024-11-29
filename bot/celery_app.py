import os
from dotenv import load_dotenv
from celery import Celery
from celery.beat import Service
from celery.schedules import crontab

from main import send_report_message


load_dotenv()


app = Celery('tasks', broker=os.getenv('CELERY_BROKER_URL'), backend=os.getenv('CELERY_RESULT_BACKEND'))


REPORT_MINUTE = os.getenv("REPORT_MINUTE")
REPORT_HOUR = os.getenv("REPORT_HOUR")

app.conf.beat_schedule = {
    'report_task': {
        'task': 'main.send_report_message',
        'schedule': crontab(hour=REPORT_HOUR, minute=REPORT_MINUTE),
    },
}

app.conf.broker_connection_retry_on_startup = True
app.conf.timezone = 'Europe/Samara'