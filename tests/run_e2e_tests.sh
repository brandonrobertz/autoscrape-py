#!/bin/bash

source tests/common.sh

die () {
  echo "${*}"
  exit 1
}

rm -f ${BENCHMARK_LOG}
./tests/crawltest.sh && ./tests/formsubmittest.sh \
  || die "Tests failed."

echo "Tests complete!"

cat ${BENCHMARK_LOG}
