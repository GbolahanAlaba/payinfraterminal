# payinfra/celery.py

import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "payinfra.settings.dev")

celery_app = Celery("payinfra")

celery_app.config_from_object("django.conf:settings", namespace="CELERY")

celery_app.autodiscover_tasks()

beat_schedule = {
    "verify-processing-transactions": {
        'task': 'api.tasks.verify_payment.verify_processing_transactions',
        'schedule': crontab(minute="*"), 
        'options': {'queue': 'celery'}
    },
}


celery_app.conf.beat_schedule = beat_schedule