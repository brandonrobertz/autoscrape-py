import os
import json

from celery import Celery
from celery.result import AsyncResult
from celery.task.control import revoke

from .scrapers.manual import ManualControlScraper


app = Celery(
    'tasks',
    broker=os.environ["CJW_RABBITMQ_HOST"],
    backend='rpc://'
)

app.conf.update(
    #CELERYD_MAX_TASKS_PER_CHILD=1,
    #CELERYD_PREFETCH_MULTIPLIER=1,
    #CELERY_ACKS_LATE=True,
    #CELERY_RESULT_PERSISTENT=True,
    #CELERY_TASK_PUBLISH_RETRY=False,
    #CELERY_TASK_RESULT_EXPIRES=None,
    CELERY_TRACK_STARTED=True,
)

@app.task()
def start(baseurl, args):
    print("Starting ManualControlScraper", baseurl, args)
    scraper = ManualControlScraper(baseurl, **args)
    scraper.run()

@app.task(bind=True)
def stop(self, id):
    print("Stopping AutoScrape job: %s" % id)
    revoke(id, terminate=True, signal='SIGKILL')

