#!/usr/bin/env python3
import base64
import os

from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy

import autoscrape.tasks as tasks

from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database


connect_str = 'postgresql://%s:%s@%s/autoscrape' % (
    os.environ["CJW_DB_USER"],
    os.environ["CJW_DB_PASSWORD"],
    os.environ["CJW_DB_HOST"]
)

engine = create_engine(connect_str)
if not database_exists(engine.url):
    create_database(engine.url)

print(database_exists(engine.url))

app = Flask("autoscrape-server", static_url_path="")
app.config['SQLALCHEMY_DATABASE_URI'] = connect_str
db = SQLAlchemy(app)


class Data(db.Model):
    """
    Store our scrape data here, indexed by the scrape ID,
    timestamp and fileclass.
    """
    __tablename__ = "data"
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        nullable=False
    )
    task_id = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    fileclass = db.Column(db.String, nullable=False)
    data = db.Column(db.String, nullable=False)

    def __init__(self, task_id, name, fileclass, data):
        self.task_id = task_id
        self.name = name
        self.fileclass = fileclass
        self.data = data

    def __repr__(self):
        return '<Data %r, %r>' % (self.name, self.fileclass)

@app.route("/start", methods=["POST"])
def post_start():
    """
    This is the main endpoint for starting AutoScrape processes. This
    endpoint simply accepts the standard parameters as a JSON payload.
    Returns a status message and the scrape task ID, which can be used
    to query status or stop the scrape.

    Curl Example:
        curl http://localhost:5000/start -H 'content-type: application/json' --data '{"baseurl": "https://bxroberts.org", "form_submit_wait": "5", "input": null, "save_graph": false, "load_images": false, "maxdepth": "0", "next_match": "next page", "leave_host": false, "show_browser": false, "driver": "Firefox", "form_submit_natural_click": false, "formdepth": "0", "link_priority": null, "keep_filename": false, "ignore_links": null, "form_match": null, "save_screenshots": true, "remote_hub": "http://localhost:4444/wd/hub", "loglevel": "DEBUG", "output": "http://flask:5001/receive/<JOB-ID-HERE>", "disable_style_saving": false}'

    Success Returns:
        HTTP 200 OK
        {"status": "OK", "data": "SCRAPE-ID"}
    """
    app.logger.debug("Starting AutoScrape job")
    args = request.get_json()
    app.logger.debug("Arguments: %s" % args)
    baseurl = args.pop("baseurl")
    app.logger.debug("Baseurl: %s" % baseurl)
    result = tasks.start.apply_async((baseurl, args))
    app.logger.debug("Result: %s" % result)
    return jsonify({"status": "OK", "data": result.id})

@app.route("/status/<id>", methods=["GET"])
def get_status(id):
    """
    Get status about a running AutoScrape task specified by
    its task ID.

    HTTP GET /status/SCRAPE-ID

    Success Returns:
        HTTP 200 OK
        {"status": "OK", "data": "STARTED"}
    """
    result = tasks.app.AsyncResult(id)
    data = Data.query.filter_by(
        task_id=id,
        fileclass="screenshot"
    ).order_by(
        Data.timestamp.desc()
    ).first()
    app.logger.debug("Task state: %s" % result.state)
    response = {
        "status": "OK",
        "message": result.state,
    }
    if data and data.data:
        app.logger.debug("Data: %s" % data)
        response["data"] = data.data
    return jsonify(response)

@app.route("/stop/<id>", methods=["POST"])
def get_stop(id):
    """
    Stop a running AutoScrape task specified by a task ID.

    HTTP POST /stop/SCRAPE-ID
        [no data required]

    Success Returns:
        HTTP 200 OK
        {"status": "OK"}
    """
    app.logger.debug("Stopping scraper task: %s" % id)
    tasks.stop.delay(id)
    return jsonify({"status": "OK"})

@app.route("/receive/<id>", methods=["POST"])
def receive_data(id):
    """
    This is a callback endpoint for receiving scrape data from
    a running AutoScrape instance, configured to send its data
    to this endpoint.

    HTTP POST /receive
        {
            "name": "crawl_data/some_file_name.html",
            "data": "base64-encoded-file-data",
            "fileclass": "crawl_data|screenshots|downloads|..."
        }
    """
    app.logger.debug("Task ID : %s" % id)
    try:
        args = request.get_json()
        name = args["name"]
        app.logger.debug("Name: %s" % name)
        fileclass = args["fileclass"]
        app.logger.debug("File class: %s" % fileclass)
        data = args["data"]
        app.logger.debug("Data: %s" % len(data))
        # app.logger.debug("Decoded: %s" % decoded)
    except Exception as e:
        app.logger.debug("Error parsing POST JSON: %s" % e)
        data = None
        fileclass = None

    # TODO: write b64 data to postgres under task ID key
    scraped_data = Data(id, name, fileclass, data)
    db.session.add(scraped_data)
    db.session.commit()
    app.logger.debug("Updated task state")

    # TODO: store/dispatch this data somewhere
    return jsonify({"status": "OK"})


if __name__ == "__main__":
    db.create_all()
    app.run(host='0.0.0.0', port=5001, debug=True)

