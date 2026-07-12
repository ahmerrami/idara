#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

COMPOSE_FILE="docker-compose.prod.yml"
COMPOSE_OVERRIDE_FILE="docker-compose.prod.override.yml"

usage() {
    cat << 'EOF'
Usage:
    bash scripts/deploy-manual-prod.sh build-push [env_file]
    bash scripts/deploy-manual-prod.sh deploy-prod [env_file]

Commands:
  build-push   Build production image and push it to Docker Hub from dev machine.
  deploy-prod  Prepare DEPLOY_PATH, pull image, and start production stack on prod server.

Examples:
    bash scripts/deploy-manual-prod.sh build-push .env.localtest
    bash scripts/deploy-manual-prod.sh deploy-prod .env.prod
EOF
}

require_cmd() {
    local cmd="$1"
    if ! command -v "$cmd" >/dev/null 2>&1; then
        echo "Required command not found: $cmd"
        exit 1
    fi
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

resolve_env_file() {
    local requested="$1"
    if [ -f "$requested" ]; then
        echo "$requested"
        return
    fi

    if [ -f .env.prod ]; then
        echo ".env.prod"
        return
    fi

    if [ -f .env.localtest ]; then
        echo ".env.localtest"
        return
    fi

    echo ""
}

write_compose_override() {
    local target_dir="$1"
    cat > "$target_dir/$COMPOSE_OVERRIDE_FILE" << 'EOF'
services:
  web:
    volumes:
      - ./media:/app/src/media
EOF
}

build_and_push() {
    local env_file="$1"

    require_cmd docker
    require_vars DOCKERHUB_USERNAME TAG

    local image="$DOCKERHUB_USERNAME/idara:$TAG"

    echo "Using env file: $env_file"
    echo "Building image: $image"
    docker build -f Dockerfile.prod -t "$image" .

    echo "Pushing image: $image"
    docker push "$image"

    echo "Image pushed successfully."
}

deploy_on_production() {
    local env_file="$1"

    require_cmd docker
    require_vars \
        DOCKERHUB_USERNAME TAG DEPLOY_PATH \
        DJANGO_SECRET_KEY DJANGO_ALLOWED_HOSTS \
        POSTGRES_DB POSTGRES_USER POSTGRES_PASSWORD DATABASE_URL

    if [ ! -f "$COMPOSE_FILE" ]; then
        echo "Missing $COMPOSE_FILE in project root."
        exit 1
    fi

    mkdir -p "$DEPLOY_PATH"
    if [ ! -w "$DEPLOY_PATH" ]; then
        echo "No write permission on '$DEPLOY_PATH'."
        echo "Run: sudo mkdir -p '$DEPLOY_PATH' && sudo chown -R '$USER':'$USER' '$DEPLOY_PATH'"
        exit 1
    fi

    mkdir -p "$DEPLOY_PATH/media"

    cp "$COMPOSE_FILE" "$DEPLOY_PATH/$COMPOSE_FILE"
    cp "$env_file" "$DEPLOY_PATH/.env.prod"
    write_compose_override "$DEPLOY_PATH"

    cd "$DEPLOY_PATH"

    ensure_postgres_volume

    echo "Pulling image from Docker Hub..."
    docker compose -f "$COMPOSE_FILE" -f "$COMPOSE_OVERRIDE_FILE" --env-file .env.prod pull web

    echo "Starting production stack..."
    docker compose -f "$COMPOSE_FILE" -f "$COMPOSE_OVERRIDE_FILE" --env-file .env.prod up -d --remove-orphans

    echo "Deployment status:"
    docker compose -f "$COMPOSE_FILE" -f "$COMPOSE_OVERRIDE_FILE" --env-file .env.prod ps

    echo "Production deployment finished."
}

main() {
    local command="${1:-}"
    local requested_env_file="${2:-.env.prod}"

    if [ -z "$command" ]; then
        usage
        exit 1
    fi

    cd "$PROJECT_ROOT"

    local env_file
    env_file="$(resolve_env_file "$requested_env_file")"
    if [ -z "$env_file" ]; then
        echo "Environment file not found. Expected '$requested_env_file', '.env.prod', or '.env.localtest'."
        exit 1
    fi

    load_env_file "$env_file"

    case "$command" in
        build-push)
            build_and_push "$env_file"
            ;;
        deploy-prod)
            deploy_on_production "$env_file"
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
