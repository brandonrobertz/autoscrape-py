#!/bin/bash

die () {
  echo "${*}"
  exit 1
}

for browser in requests selenium; do
  output="autoscrape-data-${browser}"
  rm -rf ${output}
  time ./scrape.py --browser-type ${browser} --keep-filename\
    --loglevel DEBUG --output ${output} \
    https://bxroberts.org || die "Backend ${browser} failed crawling."
done

