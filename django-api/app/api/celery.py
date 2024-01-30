from __future__ import absolute_import, unicode_literals

import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.settings")

app = Celery("api")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# Every 10 minutes
app.conf.beat_schedule = {
    "get_data_10_min": {
        "task": "wildfiresapi.tasks.get_data",
        "schedule": 600,
    },
}
