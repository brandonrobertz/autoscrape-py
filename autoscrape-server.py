#!/usr/bin/env python3
import base64
from flask import Flask, request, jsonify

import autoscrape.tasks as tasks


app = Flask(__name__)


@app.route("/", methods=["GET"])
def get_root():
    return jsonify({"status": "OK", "message": "Welcome to AutoScrape"})

@app.route("/start", methods=["POST"])
def post_start():
    """
    This is the main endpoint for starting AutoScrape processes. This
    endpoint simply accepts the standard parameters as a JSON payload.
    Returns a status message and the scrape task ID, which can be used
    to query status or stop the scrape.

    Curl Example:
        curl http://localhost:5000/start -H 'content-type: application/json' --data '{"baseurl": "https://bxroberts.org", "form_submit_wait": "5", "input": null, "save_graph": false, "load_images": false, "maxdepth": "0", "next_match": "next page", "leave_host": false, "show_browser": false, "driver": "Firefox", "form_submit_natural_click": false, "formdepth": "0", "link_priority": null, "keep_filename": false, "ignore_links": null, "form_match": null, "save_screenshots": false, "remote_hub": "http://localhost:4444/wd/hub", "loglevel": "DEBUG", "output_data_dir": "http://localhost:5000/receive", "disable_style_saving": false}'

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
    return jsonify({"status": "OK", "data": result.state})

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
    tasks.stop.delay(id)
    return jsonify({"status": "OK"})

@app.route("/receive", methods=["POST"])
def receive_data():
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
    try:
        args = request.get_json()
        app.logger.debug("Name: %s" % args["name"])
        app.logger.debug("File class: %s" % args["fileclass"])
        data = args["data"]
        app.logger.debug("Data: %s" % len(data))
        decoded = base64.b64decode(bytes(data, "utf-8")).decode("utf-8")
        # app.logger.debug("Decoded: %s" % decoded)
    except Exception as e:
        app.logger.debug("Error parsing POST JSON: %s" % e)
        args = request.data

    # TODO: store/dispatch this data somewhere
    return jsonify({"status": "OK"})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

