#!/bin/bash

time ./autoscrape.py \
  --maxdepth 10 \
  --loglevel DEBUG \
  --backend warc \
  --warc-directory training_data/common-crawl/filtered/ \
  --warc-index-file /tmp/level.db \
  --output '' \
  'http://calendar.uconn.edu/2017/day/065/433/'

rm -rf /tmp/level.db
