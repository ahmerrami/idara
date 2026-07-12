#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

COMPOSE_FILE="docker-compose.prod.yml"
PROJECT_NAME="${COMPOSE_PROJECT_NAME:-idara-localtest}"

usage() {
    cat << 'EOF'
Usage:
    bash scripts/prodlike-local.sh up [env_file]
    bash scripts/prodlike-local.sh down [env_file]
    bash scripts/prodlike-local.sh ps [env_file]
    bash scripts/prodlike-local.sh logs [env_file]

Commands:
  up    Build image locally and start local test stack.
  down  Stop and remove local test stack.
  ps    Show local test stack status.
  logs  Follow web container logs.

Examples:
    bash scripts/prodlike-local.sh up .env.localtest
    bash scripts/prodlike-local.sh logs .env.localtest
    bash scripts/prodlike-local.sh down .env.localtest
EOF
}

load_env_file() {
    local file="$1"
    while IFS= read -r line || [ -n "$line" ]; do
        line="${line%$'\r'}"

        [ -z "$line" ] && continue
        case "$line" in
            \#*) continue ;;
        esac

        if [[ "$line" != *=* ]]; then
            continue
        fi

        local key="${line%%=*}"
        local value="${line#*=}"

        if [[ ! "$key" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]]; then
            continue
        fi

        export "$key=$value"
    done < "$file"
}

ensure_postgres_volume() {
    local volume_name="${POSTGRES_VOLUME_NAME:-idara_prod_postgres_data}"
    docker volume create "$volume_name" >/dev/null
}

resolve_env_file() {
    local requested="$1"
    if [ -f "$requested" ]; then
        echo "$requested"
        return
    fi

    if [ -f .env.localtest ]; then
        echo ".env.localtest"
        return
    fi

    if [ -f .env.prod ]; then
        echo ".env.prod"
        return
    fi

    echo ""
}

require_vars() {
    local missing=0
    for var_name in "$@"; do
        if [ -z "${!var_name:-}" ]; then
            echo "Missing required variable: $var_name"
            missing=1
        fi
    done

    if [ "$missing" -ne 0 ]; then
        exit 1
    fi
}

compose() {
    local env_file="$1"
    shift
    docker compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" --env-file "$env_file" "$@"
}

main() {
    local command="${1:-}"
    local requested_env_file="${2:-.env.localtest}"

    if [ -z "$command" ]; then
        usage
        exit 1
    fi

    cd "$PROJECT_ROOT"

    local env_file
    env_file="$(resolve_env_file "$requested_env_file")"
    if [ -z "$env_file" ]; then
        echo "Environment file not found. Expected '$requested_env_file', '.env.localtest', or '.env.prod'."
        exit 1
    fi

    load_env_file "$env_file"
    require_vars DOCKERHUB_USERNAME TAG

    local image="$DOCKERHUB_USERNAME/idara:$TAG"

    case "$command" in
        up)
            echo "Building local image: $image"
            docker build -f Dockerfile.prod -t "$image" .
            ensure_postgres_volume
            echo "Starting local test stack ($PROJECT_NAME)..."
            compose "$env_file" up -d --force-recreate
            echo "Local test URL: http://localhost:8000/"
            compose "$env_file" ps
            ;;
        down)
            compose "$env_file" down -v
            ;;
        ps)
            compose "$env_file" ps
            ;;
        logs)
            compose "$env_file" logs -f web
            ;;
        -h|--help|help)
            usage
            ;;
        *)
            echo "Unknown command: $command"
            usage
            exit 1
            ;;
    esac
}

main "$@"
