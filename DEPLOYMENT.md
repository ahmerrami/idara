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

## Alternative Deployment Via deploy-manual-prod.sh

Use this alternative when you want a simple and repeatable production deployment without building images on the production server.

How it works:
- Build and push the Docker image from the development machine.
- On the production machine, only pull the published image and start services.

Why use this alternative:
- No Docker build toolchain needed on production.
- Faster redeploys (pull + restart only).
- Same script for first deployment and updates.

### Step 1 (development machine): build and push

```bash
bash scripts/deploy-manual-prod.sh build-push .env.localtest
```

Required variables in the env file for this step:
- `DOCKERHUB_USERNAME`
- `TAG`

### Step 2 (production machine): deploy from Docker Hub

```bash
git clone <your-repo-url> idara
cd idara
cp .env.prod.example .env.prod
```

Edit `.env.prod` with real values, at least:
- `DEPLOY_PATH` (example: `/opt/idara`)
- `DOCKERHUB_USERNAME`, `TAG`
- `DJANGO_SECRET_KEY`
- `DJANGO_ALLOWED_HOSTS`
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- `POSTGRES_VOLUME_NAME`
- `DATABASE_URL` (must match `POSTGRES_*`)

Then run:

```bash
bash scripts/deploy-manual-prod.sh deploy-prod .env.prod
```

What `deploy-prod` does automatically:
- validates required variables
- creates `DEPLOY_PATH` and `DEPLOY_PATH/media`
- copies `docker-compose.prod.yml` and `.env.prod` to `DEPLOY_PATH`
- generates `docker-compose.prod.override.yml` (media mount)
- creates the external PostgreSQL volume if missing
- pulls `DOCKERHUB_USERNAME/idara:TAG`
- starts/updates `db` and `web` with Compose
- prints final service status (`docker compose ps`)

Important:
- This workflow does not build images on the production server.
- Data persists in Docker volume (`POSTGRES_VOLUME_NAME`) and `DEPLOY_PATH/media`.

## Quick manual workflow (recommended)

Use the new script in two steps:

1) On development machine (build + push image):

```bash
bash scripts/deploy-manual-prod.sh build-push .env.localtest
```

2) On production server, run this checklist in order:

```bash
git clone <your-repo-url> idara
cd idara
cp .env.prod.example .env.prod
```

3) Edit `.env.prod` on the production server with real values:
- `DEPLOY_PATH` (example: `/opt/idara`)
- `DOCKERHUB_USERNAME` and `TAG`
- `DJANGO_SECRET_KEY`
- `DJANGO_ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS` if the app is served behind a real domain over HTTPS
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- `POSTGRES_VOLUME_NAME`
- `DATABASE_URL` (must match the `POSTGRES_*` values)

4) Verify Docker is available on the production server:

```bash
docker --version
docker compose version
```

5) On production server, run the deployment script:

```bash
bash scripts/deploy-manual-prod.sh deploy-prod .env.prod
```

The `deploy-prod` command will:
- require `docker` and Docker Compose on the production machine
- create `DEPLOY_PATH` if needed
- create `DEPLOY_PATH/media`
- copy `docker-compose.prod.yml` and `.env.prod` into `DEPLOY_PATH`
- generate `docker-compose.prod.override.yml` to mount media volume
- create the external PostgreSQL volume if it does not exist yet
- pull the `web` image from Docker Hub
- start the `db` and `web` containers with Docker Compose
- recreate/update the stack in `DEPLOY_PATH`
- show `docker compose ps` at the end

There is no image build on the production server in this workflow. The production server only pulls the published `web` image from Docker Hub and creates/starts the containers locally.

Production server checklist summary:

1) Clone the repository on the target machine.
2) Create `.env.prod` from `.env.prod.example`.
3) Fill in the real production values.
4) Verify `docker` and Docker Compose are installed.
5) Run `bash scripts/deploy-manual-prod.sh deploy-prod .env.prod`.
6) Check the final `ps` output and then inspect logs if needed.

## Run On Another Local Machine (using Docker image)

Use this when you want to run the app on a second machine in local mode (same LAN or standalone), by pulling an image from Docker Hub.

1) On your current machine (build and push image):

```bash
bash scripts/deploy-manual-prod.sh build-push .env.localtest
```

2) On the other machine:

```bash
git clone <your-repo-url> idara
cd idara
cp .env.prod.example .env.prod
```

3) Edit `.env.prod` on the other machine:
- `DOCKERHUB_USERNAME` and `TAG`
- `DJANGO_SECRET_KEY`
- `DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1`
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- `DATABASE_URL` (must match POSTGRES_* values)
- `DEPLOY_PATH` (example: `/opt/idara`)

4) Pull and run:

```bash
bash scripts/deploy-manual-prod.sh deploy-prod .env.prod
```

5) Test in browser on that machine:

```text
http://localhost:8000
```

Notes:
- Data persistence is kept for DB (external Docker volume `POSTGRES_VOLUME_NAME`) and media (`DEPLOY_PATH/media`).
- For local tests without HTTPS, keep `DJANGO_SECURE_SSL_REDIRECT=false` in `.env.prod`.

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
- `CSRF_TRUSTED_ORIGINS` if the app is served behind a real domain over HTTPS
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- `POSTGRES_VOLUME_NAME` (example: `idara_prod_postgres_data`)
- `DATABASE_URL`

## 4) Run in production mode

If you do not use `scripts/deploy-manual-prod.sh`, you must perform the equivalent production-server steps yourself:

1) Copy the required files to the target directory on the production machine:
- `docker-compose.prod.yml`
- `.env.prod`
- a `docker-compose.prod.override.yml` file that mounts `./media:/app/src/media`

2) Create the external PostgreSQL volume:

```bash
docker volume create ${POSTGRES_VOLUME_NAME}
```

3) Pull the application image from Docker Hub:

```bash
docker compose -f docker-compose.prod.yml -f docker-compose.prod.override.yml --env-file .env.prod pull web
```

4) Start the production stack:

```bash
docker compose -f docker-compose.prod.yml -f docker-compose.prod.override.yml --env-file .env.prod up -d --remove-orphans
```

## 5) Useful commands

Check logs:

```bash
docker compose -f docker-compose.prod.yml -f docker-compose.prod.override.yml --env-file .env.prod logs -f web
```

Stop stack:

```bash
docker compose -f docker-compose.prod.yml -f docker-compose.prod.override.yml --env-file .env.prod down
```

Do not use `down -v` in production unless you explicitly want to remove database data.

## Notes

- The image runs Django with `config.settings.production`.
- On startup, the container runs migrations and collectstatic automatically.
- Use a strong random value for `DJANGO_SECRET_KEY`.
- PostgreSQL data uses an external Docker volume (`POSTGRES_VOLUME_NAME`) and survives container removal.
- Media files are bind-mounted to `DEPLOY_PATH/media` via `docker-compose.prod.override.yml` and survive container removal.
- The provided production compose file does not include Nginx, Traefik, or TLS termination. For Internet-facing deployment, run this stack behind a reverse proxy that forwards `X-Forwarded-Proto=https`.
