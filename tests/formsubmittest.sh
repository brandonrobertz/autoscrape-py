#!/bin/bash

URL="https://utdirect.utexas.edu/apps/degree/degrees/nlogon/"

./scrape.py \
  --backend selenium \
  --show-browser \
  --form-match "List students starting from" \
  --input "i:1:SMITH\, JOHN" \
  --next-match "Next Page" \
  --loglevel DEBUG \
  ${URL}

