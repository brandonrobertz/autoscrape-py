#!/bin/bash

for browser in requests selenium; do
  output="autoscrape-data-${browser}"
  rm -rf ${output}
  time ./scrape.py --browser-type ${browser} --keep-filename\
    --loglevel DEBUG --output ${output} \
    https://bxroberts.org
done

