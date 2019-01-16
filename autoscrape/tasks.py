import os
import json

from celery import Celery
from celery.result import AsyncResult
from celery.task.control import revoke

from .scrapers.manual import ManualControlScraper


app = Celery(
    'tasks',
    broker=os.environ["CJW_RABBITMQ_HOST"],
    backend='rpc://' #os.environ["CJW_RABBITMQ_HOST"]
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

