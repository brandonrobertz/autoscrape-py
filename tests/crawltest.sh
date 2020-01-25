#!/bin/bash

die () {
  echo "${*}"
  exit 1
}

for browser in requests selenium; do
  output="autoscrape-data-${browser}"
  rm -rf ${output}
  echo "=================================================="
  echo "Running ${browser} crawl"
  time ./scrape.py \
    --backend ${browser} \
    --keep-filename\
    --loglevel DEBUG \
    --output ${output} \
    https://bxroberts.org \
    || die "Backend ${browser} failed crawling."
  echo "${browser} crawl complete!"
done

