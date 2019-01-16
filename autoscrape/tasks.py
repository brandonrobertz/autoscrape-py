import os
import json

from celery import Celery

from .scrapers.manual import ManualControlScraper


app = Celery(
    'tasks',
    broker=os.environ["CJW_RABBITMQ_HOST"]
)

@app.task()
def start(baseurl, args):
    print("Starting ManualControlScraper", baseurl, args)
    scraper = ManualControlScraper(baseurl, **args)
    scraper.run()

@app.task(bind=True)
def stop(self, id):
    print("Stopping AutoScrape job: %s" % id)
    return "STOPPED"

@app.task(bind=True)
def status(self, id):
    print("Getting status for AutoScrape job: %s" % id)
    return "OK"

