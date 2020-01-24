#!/bin/bash

for browser in requests selenium; do
  rm -rf autoscrape-data-${browser}
  ./scrape.py --browser-type ${browser} --keep-filename https://bxroberts.org --loglevel DEBUG --output autoscrape-data${browser}-
done
