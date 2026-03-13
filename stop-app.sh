#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if ! command -v docker >/dev/null 2>&1; then
  echo "docker is required but was not found in PATH"
  exit 1
fi

DOCS_PORT="${DOCS_PORT:-8081}"
export DOCS_PORT

DOCS_REPO_DEFAULT="$(cd "${ROOT_DIR}/.." && pwd)/veterinary-medical-records-documentation"
DOCS_REPO_WORKTREE="$(cd "${ROOT_DIR}/../.." && pwd)/veterinary-medical-records-documentation"

if [[ -d "${DOCS_REPO_DEFAULT}" ]]; then
  DOCS_REPO_PATH="${DOCS_REPO_DEFAULT}"
  export DOCS_REPO_PATH
elif [[ -d "${DOCS_REPO_WORKTREE}" ]]; then
  DOCS_REPO_PATH="${DOCS_REPO_WORKTREE}"
  export DOCS_REPO_PATH
fi

docker compose -f "${ROOT_DIR}/docker-compose.yml" -f "${ROOT_DIR}/docker-compose.evaluators.yml" down "$@"
