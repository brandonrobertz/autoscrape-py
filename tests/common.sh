OUTPUT_BASE="autoscrape-data-tests"
BENCHMARK_LOG="${OUTPUT_BASE}/backend-benchmark.log"
BACKENDS="selenium requests"
TIME="$(which time) -p -a -o ${BENCHMARK_LOG}"

AUTOSCRAPE="./autoscrape.py --save-graph --loglevel DEBUG"

mkdir -p ${OUTPUT_BASE}

die () {
  echo "${*}"
  exit 1
}

add_benchmark_header () {
  benchmark="${1}"
  crawlname="${2}"
  echo "Running ${benchmark} ${crawlname}" | tee -a ${BENCHMARK_LOG}
}

