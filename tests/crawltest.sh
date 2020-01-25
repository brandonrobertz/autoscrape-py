#!/bin/bash

source tests/common.sh

for backend in ${BACKENDS}; do
  output="autoscrape-data-${backend}"
  rm -rf ${output}
  echo "=================================================="
  add_benchmark_header ${backend} "crawl"
  ${TIME} ./scrape.py \
    --backend ${backend} \
    --keep-filename\
    --loglevel DEBUG \
    --output ${output} \
    https://bxroberts.org \
    || die "Backend ${backend} failed crawling."
  echo "${backend} crawl complete!"
done

