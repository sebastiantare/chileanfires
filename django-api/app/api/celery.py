from __future__ import absolute_import, unicode_literals

import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.settings")

app = Celery("api")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):

    # Executes the task every 10 minutes
    sender.add_periodic_task(
        crontab(minute='*/10'),
        get_data.s(),
        name='get_data',
    )
