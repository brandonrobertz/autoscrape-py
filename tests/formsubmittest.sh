#!/bin/bash
URL="https://utdirect.utexas.edu/apps/degree/degrees/nlogon/"

source tests/common.sh

for backend in ${BACKENDS}; do
  output="${OUTPUT_BASE}/autoscrape-data-formsubmit-${backend}"
  rm -rf ${output}
  add_separator
  add_benchmark_header ${backend} "form submitter"
  ${TIME} ${AUTOSCRAPE} \
    --backend ${backend} \
    --maxdepth 1 \
    --formdepth 1 \
    --form-match "List students starting from" \
    --input "i:0:SMITH\, JOHN" \
    --next-match "Next Page" \
    --output ${output} \
    ${URL} \
    || die "Backend ${backend} failed submitting forms"
done

