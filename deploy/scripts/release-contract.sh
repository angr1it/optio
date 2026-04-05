#!/usr/bin/env bash
set -euo pipefail

output_file="${GITHUB_OUTPUT:-/dev/stdout}"
input_tag="${INPUT_TAG:-}"

if [[ -n "${input_tag}" ]]; then
  image_tag="${input_tag}"
elif [[ "${GITHUB_REF_TYPE:-}" == "tag" ]]; then
  image_tag="${GITHUB_REF_NAME}"
else
  image_tag="sha-${GITHUB_SHA:0:12}"
fi

if [[ "${image_tag}" =~ ^v([0-9]+)\.([0-9]+)\.([0-9]+)(-([0-9A-Za-z-]+(\.[0-9A-Za-z-]+)*))?$ ]]; then
  if [[ "${GITHUB_REF_TYPE:-}" != "tag" || "${GITHUB_REF_NAME:-}" != "${image_tag}" ]]; then
    echo "SemVer release artifacts must come from a matching Git tag ref."
    echo "Run this workflow from tag ${image_tag}, or use sha-<12 hex> for manual builds."
    exit 1
  fi
  chart_version="${BASH_REMATCH[1]}.${BASH_REMATCH[2]}.${BASH_REMATCH[3]}${BASH_REMATCH[4]}"
  if [[ -z "${BASH_REMATCH[4]}" ]]; then
    semver_minor="${BASH_REMATCH[1]}.${BASH_REMATCH[2]}"
  else
    semver_minor=""
  fi
  is_release_tag=true
elif [[ "${image_tag}" =~ ^sha-([0-9a-f]{12})$ ]]; then
  chart_version="0.0.0-${BASH_REMATCH[1]}"
  semver_minor=""
  is_release_tag=false
else
  echo "Unsupported image tag: ${image_tag}"
  echo "Use v0.1.0 or v0.1.0-rc.1, or an immutable sha tag like sha-0123abcd4567."
  exit 1
fi

echo "image_tag=${image_tag}" >>"${output_file}"
echo "chart_version=${chart_version}" >>"${output_file}"
echo "semver_minor=${semver_minor}" >>"${output_file}"
echo "is_release_tag=${is_release_tag}" >>"${output_file}"
