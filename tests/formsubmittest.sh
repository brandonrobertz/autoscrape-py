#!/bin/bash
URL="https://utdirect.utexas.edu/apps/degree/degrees/nlogon/"

die () {
  echo "${*}"
  exit 1
}

for browser in requests selenium; do
  output="autoscrape-data-formsubmit-${browser}"
  rm -rf ${output}
  time ./scrape.py \
    --backend ${browser} \
    --maxdepth 1 \
    --formdepth 1 \
    --form-match "List students starting from" \
    --input "i:0:SMITH\, JOHN" \
    --next-match "Next Page" \
    --loglevel DEBUG \
    --output ${output} \
    ${URL} \
    || die "Backend ${browser} failed submitting forms"
done

