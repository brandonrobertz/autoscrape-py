# -*- coding: UTF-8 -*-
import os
import re

from celery import Celery

from .scrapers.manual import ManualControlScraper


backend = "rpc://"
if os.environ.get("AUTOSCRAPE_DB_HOST"):
    backend = 'db+postgresql://%s:%s@%s/autoscrape' % (
        os.environ["AUTOSCRAPE_DB_USER"],
        os.environ["AUTOSCRAPE_DB_PASSWORD"],
        os.environ["AUTOSCRAPE_DB_HOST"]
    )


app = Celery(
    'tasks',
    broker=os.environ.get("AUTOSCRAPE_RABBITMQ_HOST"),
    backend=backend,
)

app.conf.update(
    # CELERYD_MAX_TASKS_PER_CHILD=1,
    # CELERYD_PREFETCH_MULTIPLIER=1,
    # CELERY_ACKS_LATE=True,
    # CELERY_RESULT_PERSISTENT=True,
    # CELERY_TASK_PUBLISH_RETRY=False,
    # CELERY_TASK_RESULT_EXPIRES=None,
    CELERY_TRACK_STARTED=True,
    CELERY_BROKER_HEARTBEAT=10
)


@app.task(bind=True)
def start(self, baseurl, args):
    print("Starting ManualControlScraper", baseurl, args)
    # append task ID to receiver URI
    output = args.get("output")
    if output and re.match("^https?://", output):
        if output[-1] != "/":
            output += "/"
        output += str(self.request.id)
        args["output"] = output
    scraper = ManualControlScraper(baseurl, **args)
    scraper.run()
