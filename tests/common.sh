BENCHMARK_LOG=backend-benchmark.log
BACKENDS="selenium requests"
TIME="$(which time) -p -a -o ${BENCHMARK_LOG}"
echo "Invoking AutoScrape via ${SCRIPT}"

AUTOSCRAPE="./autoscrape.py --save-graph --loglevel DEBUG"

die () {
  echo "${*}"
  exit 1
}

add_benchmark_header () {
  benchmark="${1}"
  crawlname="${2}"
  echo "Running ${benchmark} ${crawlname}" | tee -a ${BENCHMARK_LOG}
}

