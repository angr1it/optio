#!/usr/bin/env bash
set -euo pipefail

: "${OPTIO_PUBLIC_URL:?Missing repository variable OPTIO_PUBLIC_URL}"

attempts="${VERIFY_ATTEMPTS:-30}"
sleep_seconds="${VERIFY_SLEEP_SECONDS:-10}"

wait_for_url() {
  local label="$1"
  local url="$2"
  local mode="$3"
  local i

  for i in $(seq 1 "${attempts}"); do
    if [[ "${mode}" == "head" ]]; then
      if curl -IfsS "${url}" >/dev/null; then
        echo "${label} is ready after ${i} attempt(s)."
        return 0
      fi
    else
      if curl -fsS "${url}" >/dev/null; then
        echo "${label} is ready after ${i} attempt(s)."
        return 0
      fi
    fi
    sleep "${sleep_seconds}"
  done

  echo "${label} did not become ready within $((attempts * sleep_seconds)) seconds: ${url}"
  return 1
}

wait_for_url "API health endpoint" "${OPTIO_PUBLIC_URL}/api/health" "get"
wait_for_url "Web endpoint" "${OPTIO_PUBLIC_URL}/" "head"
