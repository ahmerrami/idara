# Deployment (Docker Hub + Production)

## Local Development (fast)

Use local development settings with hot-reload and SQLite:

```bash
docker compose -f docker-compose.yml up -d
```

Stop local development stack:

```bash
docker compose -f docker-compose.yml down
```

## Local Testing On Development Machine

Start local test stack (prod-like, with local build):

```bash
bash scripts/prodlike-local.sh up .env.localtest
```

Follow logs:

```bash
bash scripts/prodlike-local.sh logs .env.localtest
```

Stop local test stack:

```bash
bash scripts/prodlike-local.sh down .env.localtest
```

This uses `docker-compose.prod.yml` and rebuilds `DOCKERHUB_USERNAME/idara:TAG` locally.

## Quick manual workflow (recommended)

Use the new script in two steps:

1) On development machine (build + push image):

```bash
bash scripts/deploy-manual-prod.sh build-push .env.localtest
```

2) On production server (pull + start stack + media folder):

```bash
bash scripts/deploy-manual-prod.sh deploy-prod .env.prod
```

The `deploy-prod` command will:
- create `DEPLOY_PATH` if needed
- create `DEPLOY_PATH/media`
- copy `docker-compose.prod.yml` and `.env.prod` into `DEPLOY_PATH`
- generate `docker-compose.prod.override.yml` to mount media volume
- pull the `web` image from Docker Hub
- start containers, network, and database with Docker Compose

## 1) Build the production image

```bash
docker build -f Dockerfile.prod -t <dockerhub_user>/idara:<tag> .
```

Example:

```bash
docker build -f Dockerfile.prod -t myuser/idara:1.0.0 .
```

## 2) Push to Docker Hub

```bash
docker login
docker push <dockerhub_user>/idara:<tag>
```

## 3) Prepare production environment variables

```bash
cp .env.prod.example .env.prod
```

Edit `.env.prod` with real values:
- `DOCKERHUB_USERNAME`
- `TAG`
- `DJANGO_SECRET_KEY`
- `DJANGO_ALLOWED_HOSTS`
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- `POSTGRES_VOLUME_NAME` (example: `idara_prod_postgres_data`)
- `DATABASE_URL`

## 4) Run in production mode

```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

## 5) Useful commands

Check logs:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod logs -f web
```

Stop stack:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod down
```

Do not use `down -v` in production unless you explicitly want to remove database data.

## Notes

- The image runs Django with `config.settings.production`.
- On startup, the container runs migrations and collectstatic automatically.
- Use a strong random value for `DJANGO_SECRET_KEY`.
- PostgreSQL data uses an external Docker volume (`POSTGRES_VOLUME_NAME`) and survives container removal.
- Media files are bind-mounted to `DEPLOY_PATH/media` via `docker-compose.prod.override.yml` and survive container removal.
