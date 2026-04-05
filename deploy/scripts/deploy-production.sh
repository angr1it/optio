#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "${script_dir}/../.." && pwd)"

: "${RELEASE_TAG:?Missing release tag input RELEASE_TAG}"
: "${DO_CLUSTER_NAME:?Missing repository variable DO_CLUSTER_NAME}"
: "${OPTIO_DOMAIN:?Missing repository variable OPTIO_DOMAIN}"
: "${OPTIO_PUBLIC_URL:?Missing repository variable OPTIO_PUBLIC_URL}"
: "${EXTERNAL_DATABASE_URL:?Missing production secret EXTERNAL_DATABASE_URL}"
: "${EXTERNAL_REDIS_URL:?Missing production secret EXTERNAL_REDIS_URL}"
: "${OPTIO_ENCRYPTION_KEY:?Missing production secret OPTIO_ENCRYPTION_KEY}"
: "${AUTH_GITHUB_CLIENT_ID:?Missing production secret AUTH_GITHUB_CLIENT_ID}"
: "${AUTH_GITHUB_CLIENT_SECRET:?Missing production secret AUTH_GITHUB_CLIENT_SECRET}"
: "${GITHUB_TOKEN:?Missing GitHub token}"

owner="$(printf '%s' "${GITHUB_REPOSITORY_OWNER}" | tr '[:upper:]' '[:lower:]')"
image_base="ghcr.io/${owner}"
namespace="optio"
release="optio"

if [[ "${RELEASE_TAG}" =~ ^v([0-9]+)\.([0-9]+)\.([0-9]+)(-([0-9A-Za-z-]+(\.[0-9A-Za-z-]+)*))?$ ]]; then
  chart_version="${BASH_REMATCH[1]}.${BASH_REMATCH[2]}.${BASH_REMATCH[3]}${BASH_REMATCH[4]}"
else
  echo "release_tag must look like v0.1.0 or v0.1.0-rc.1"
  exit 1
fi

if [[ -n "${GITHUB_APP_ID:-}" ]]; then
  : "${GITHUB_APP_INSTALLATION_ID:?Missing production secret GITHUB_APP_INSTALLATION_ID when GITHUB_APP_ID is set}"
  : "${GITHUB_APP_PRIVATE_KEY:?Missing production secret GITHUB_APP_PRIVATE_KEY when GITHUB_APP_ID is set}"
fi

if [[ -n "${GITHUB_APP_CLIENT_ID:-}" || -n "${GITHUB_APP_CLIENT_SECRET:-}" ]]; then
  : "${GITHUB_APP_CLIENT_ID:?GITHUB_APP_CLIENT_ID must be set with GITHUB_APP_CLIENT_SECRET}"
  : "${GITHUB_APP_CLIENT_SECRET:?GITHUB_APP_CLIENT_SECRET must be set with GITHUB_APP_CLIENT_ID}"
fi

runner_temp="${RUNNER_TEMP:-/tmp}"
chart_root="${runner_temp}/chart"
chart_path="${chart_root}/optio"
runtime_values_path="${runner_temp}/values.runtime.yaml"

printf '%s' "${GITHUB_TOKEN}" | helm registry login ghcr.io -u "${GITHUB_ACTOR}" --password-stdin

helm pull "oci://${image_base}/optio" \
  --version "${chart_version}" \
  --untar \
  --untardir "${chart_root}"

doctl kubernetes cluster kubeconfig save "${DO_CLUSTER_NAME}"
kubectl create namespace "${namespace}" --dry-run=client -o yaml | kubectl apply -f -
kubectl label namespace "${namespace}" app.kubernetes.io/managed-by=Helm --overwrite
kubectl annotate namespace "${namespace}" meta.helm.sh/release-name="${release}" --overwrite
kubectl annotate namespace "${namespace}" meta.helm.sh/release-namespace="${namespace}" --overwrite
kubectl apply -f "${repo_root}/deploy/limitrange.yaml"

if [[ -n "${GITHUB_APP_ID:-}" ]]; then
  private_key_file="${runner_temp}/github-app.pem"
  printf '%s' "${GITHUB_APP_PRIVATE_KEY}" >"${private_key_file}"

  secret_args=(
    --from-literal=GITHUB_APP_ID="${GITHUB_APP_ID}"
    --from-literal=GITHUB_APP_INSTALLATION_ID="${GITHUB_APP_INSTALLATION_ID}"
    --from-file=GITHUB_APP_PRIVATE_KEY="${private_key_file}"
  )

  if [[ -n "${GITHUB_APP_CLIENT_ID:-}" && -n "${GITHUB_APP_CLIENT_SECRET:-}" ]]; then
    secret_args+=(--from-literal=GITHUB_APP_CLIENT_ID="${GITHUB_APP_CLIENT_ID}")
    secret_args+=(--from-literal=GITHUB_APP_CLIENT_SECRET="${GITHUB_APP_CLIENT_SECRET}")
  fi
  if [[ -n "${GITHUB_APP_BOT_NAME:-}" ]]; then
    secret_args+=(--from-literal=GITHUB_APP_BOT_NAME="${GITHUB_APP_BOT_NAME}")
  fi
  if [[ -n "${GITHUB_APP_BOT_EMAIL:-}" ]]; then
    secret_args+=(--from-literal=GITHUB_APP_BOT_EMAIL="${GITHUB_APP_BOT_EMAIL}")
  fi

  kubectl -n "${namespace}" create secret generic optio-github-app \
    "${secret_args[@]}" \
    --dry-run=client \
    -o yaml | kubectl apply -f -
else
  echo "GitHub App secrets not configured; skipping Kubernetes secret creation."
fi

python3 "${repo_root}/deploy/scripts/render-runtime-values.py" "${runtime_values_path}"

values_file="${repo_root}/deploy/values.fork-production.yaml"
if [[ ! -f "${values_file}" ]]; then
  echo "Missing fork production values file: deploy/values.fork-production.yaml"
  exit 1
fi

helm_image_args=(
  --set-string api.image.repository="${image_base}/optio-api"
  --set-string web.image.repository="${image_base}/optio-web"
  --set-string optio.image.repository="${image_base}/optio-optio"
  --set-string agent.image.repository="${image_base}/optio-agent-base"
  --set-string api.image.tag="${RELEASE_TAG}"
  --set-string web.image.tag="${RELEASE_TAG}"
  --set-string optio.image.tag="${RELEASE_TAG}"
  --set-string agent.image.tag="${RELEASE_TAG}"
)

helm lint "${chart_path}" \
  -f "${values_file}" \
  -f "${runtime_values_path}" \
  "${helm_image_args[@]}"

helm template "${release}" "${chart_path}" \
  --namespace "${namespace}" \
  -f "${values_file}" \
  -f "${runtime_values_path}" \
  "${helm_image_args[@]}" >/dev/null

helm upgrade --install "${release}" "${chart_path}" \
  --namespace "${namespace}" \
  --create-namespace \
  --history-max 10 \
  -f "${values_file}" \
  -f "${runtime_values_path}" \
  "${helm_image_args[@]}" \
  --wait \
  --timeout 15m

kubectl -n "${namespace}" rollout status deployment/"${release}"-api --timeout=5m
kubectl -n "${namespace}" rollout status deployment/"${release}"-web --timeout=5m
kubectl -n "${namespace}" rollout status deployment/"${release}"-optio --timeout=5m

helm test "${release}" --namespace "${namespace}" --timeout 5m
