#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "${script_dir}/../.." && pwd)"

: "${DO_CLUSTER_NAME:?Missing repository variable DO_CLUSTER_NAME}"
: "${LETSENCRYPT_EMAIL:?Missing repository variable LETSENCRYPT_EMAIL}"

namespace="optio"
ingress_nginx_chart_version="${INGRESS_NGINX_CHART_VERSION:-4.11.3}"
cert_manager_chart_version="${CERT_MANAGER_CHART_VERSION:-v1.16.2}"
metrics_server_chart_version="${METRICS_SERVER_CHART_VERSION:-3.12.2}"

doctl kubernetes cluster kubeconfig save "${DO_CLUSTER_NAME}"

helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo add jetstack https://charts.jetstack.io
helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server
helm repo update

helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx \
  --version "${ingress_nginx_chart_version}" \
  --namespace ingress-nginx \
  --create-namespace \
  --wait \
  --timeout 10m

helm upgrade --install cert-manager jetstack/cert-manager \
  --version "${cert_manager_chart_version}" \
  --namespace cert-manager \
  --create-namespace \
  --set crds.enabled=true \
  --wait \
  --timeout 10m

helm upgrade --install metrics-server metrics-server/metrics-server \
  --version "${metrics_server_chart_version}" \
  --namespace kube-system \
  --wait \
  --timeout 10m

kubectl create namespace "${namespace}" --dry-run=client -o yaml | kubectl apply -f -

sed "s/__LETSENCRYPT_EMAIL__/${LETSENCRYPT_EMAIL}/g" "${repo_root}/deploy/cluster-issuer.yaml" \
  | kubectl apply -f -

echo "Bootstrap complete."
echo "1. Point DNS to the ingress-nginx load balancer."
echo "2. Populate the production environment secrets and variables."
echo "3. Run the Fork Deploy Production workflow with a released image tag."
