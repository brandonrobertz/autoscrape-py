BENCHMARK_LOG=backend-benchmark.log
BACKENDS="requests selenium"
TIME="$(which time) -p -a -o ${BENCHMARK_LOG}"

die () {
  echo "${*}"
  exit 1
}

add_benchmark_header () {
  benchmark="${1}"
  crawlname="${2}"
  echo "Running ${benchmark} ${crawlname}" | tee -a ${BENCHMARK_LOG}
}
