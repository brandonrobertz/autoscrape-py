#!/bin/bash

source tests/common.sh

for backend in ${BACKENDS}; do
  output="${OUTPUT_BASE}/autoscrape-data-${backend}"
  rm -rf ${output}
  echo "=================================================="
  add_benchmark_header ${backend} "crawl"
  ${TIME} ${AUTOSCRAPE} \
    --backend ${backend} \
    --output ${output} \
    https://bxroberts.org \
    || die "Backend ${backend} failed crawling."
  echo "${backend} crawl complete!"
done

