#!/usr/bin/env python3
from flask import Flask, request, jsonify

from autoscrape.tasks import start, stop, status


app = Flask(__name__)


@app.route("/", methods=["GET"])
def get_root():
    return jsonify({"status": "OK", "message": "Welcome to AutoScrape"})

@app.route("/start", methods=["POST"])
def post_start():
    """
    Test endpoint with:
        curl http://localhost:5000/start -H 'content-type: application/json' --data '{"baseurl": "https://bxroberts.org", "form_submit_wait": "5", "input": null, "save_graph": false, "load_images": false, "maxdepth": "0", "next_match": "next page", "leave_host": false, "show_browser": false, "driver": "Firefox", "form_submit_natural_click": false, "formdepth": "0", "link_priority": null, "keep_filename": false, "ignore_links": null, "form_match": null, "save_screenshots": false, "remote_hub": "http://localhost:4444/wd/hub", "loglevel": "DEBUG", "output_data_dir": "/tmp/autoscrape-data", "disable_style_saving": false}'
    """
    print("Starting AutoScrape job")
    args = request.get_json()
    print("Args", args)
    baseurl = args.pop("baseurl")
    print("Baseurl", baseurl)
    result = start.apply_async((baseurl, args))
    print("Result", result)
    return jsonify({"status": "OK", "data": result.id})

@app.route("/status/<id>", methods=["GET"])
def get_status(id):
    result = status(id)
    return jsonify({"status": "OK", "data": result.id})

@app.route("/stop/<id>", methods=["POST"])
def get_stop(id):
    result = stop(id)
    return jsonify({"status": "OK", "data": result.id})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

