# incident-track

A FastAPI service backed by PostgreSQL for tracking incidents, with a Reddit RSS scraper.

## Stack

- **API:** FastAPI + Uvicorn
- **Database:** PostgreSQL, accessed via SQLAlchemy 2.0 (`psycopg` driver). Docker uses PostgreSQL 17; local PostgreSQL 16+ is fine for development.
- **Containerization:** Docker Compose (app + database)

## Prerequisites

- Python 3.12
- PostgreSQL, either installed locally or run through Docker Compose
- Optional: [Docker](https://docs.docker.com/get-docker/) with Compose v2 (`docker compose`) if you want the container workflow

## Quick start (Docker)

1. **Create your environment file** from the template:

   ```bash
   cp .env.example .env
   ```

   The template works out of the box for Docker development:

   ```ini
   POSTGRES_USER=incident
   POSTGRES_PASSWORD=changeme
   POSTGRES_DB=incidents
   DATABASE_URL=postgresql+psycopg://incident:changeme@db:5432/incidents
   ```

   > Change `POSTGRES_PASSWORD` if you would like

2. **Build and start the stack:**

   ```bash
   docker compose up --build
   ```

   This starts two containers:
   - `db` — PostgreSQL, published on `localhost:5432`
   - `incidenttrack` — the API, published on `localhost:8000`

   The app waits for Postgres to pass its healthcheck before starting, and creates
   the database tables on boot.

3. **Verify it's running:**

   ```bash
   curl localhost:8000/incidents   # -> []
   ```

   An empty array (not an error) means the app booted, connected to Postgres, and
   the `incidents` table exists.

To stop: `docker compose down`. To also wipe the database volume (fresh schema next
start): `docker compose down -v`.

## API endpoints

| Method | Path          | Description              |
| ------ | ------------- | ------------------------ |
| GET    | `/`           | Health/hello check       |
| GET    | `/incidents`  | List all incidents       |

Interactive docs are available at <http://localhost:8000/docs> once running.

## Local setup without Docker

This is the easiest workflow for learning and debugging because the API runs
directly on your machine and connects to a local Postgres server.

The important connection-string rule is:

```ini
# Docker Compose app connecting to Docker Compose Postgres
DATABASE_URL=postgresql+psycopg://incident:incident@db:5432/incidents

# Local app connecting to local Postgres
DATABASE_URL=postgresql+psycopg://incident:incident@localhost:5432/incidents
```

Use `db` only when the API is also running inside Docker Compose. Use `localhost`
when running the API directly on your computer.

### macOS

1. Install and start Postgres with Homebrew:

   ```bash
   brew install postgresql@16
   brew services start postgresql@16
   ```

2. Create the app database user and database:

   ```bash
   createuser --pwprompt incident
   createdb -O incident incidents
   ```

   When prompted, use `incident` as the password unless you want to choose a
   different local password.

3. Create `.env`:

   ```bash
   cp .env.example .env
   ```

   Then edit `.env` so it points at `localhost`:

   ```ini
   POSTGRES_USER=incident
   POSTGRES_PASSWORD=incident
   POSTGRES_DB=incidents
   DATABASE_URL=postgresql+psycopg://incident:incident@localhost:5432/incidents
   ```

4. Install Python dependencies and run the API:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install -r requirements.txt
   python -m uvicorn backend.main:app --reload
   ```

5. Verify it works:

   ```bash
   curl localhost:8000/incidents
   ```

### Windows

1. Install PostgreSQL from the official installer:

   <https://www.postgresql.org/download/windows/>

   During installation, remember the password you set for the default `postgres`
   admin user. If the installer asks whether to add command-line tools to `PATH`,
   enable that option.

2. Open PowerShell and create the app database user and database:

   ```powershell
   psql -U postgres
   ```

   Then run these SQL commands inside `psql`:

   ```sql
   CREATE ROLE incident WITH LOGIN PASSWORD 'incident';
   CREATE DATABASE incidents OWNER incident;
   \q
   ```

3. Create `.env`:

   ```powershell
   Copy-Item .env.example .env
   ```

   Then edit `.env` so it points at `localhost`:

   ```ini
   POSTGRES_USER=incident
   POSTGRES_PASSWORD=incident
   POSTGRES_DB=incidents
   DATABASE_URL=postgresql+psycopg://incident:incident@localhost:5432/incidents
   ```

4. Install Python dependencies and run the API:

   ```powershell
   py -3.12 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   python -m uvicorn backend.main:app --reload
   ```

   If PowerShell blocks the activation script, run this once and then try the
   activation command again:

   ```powershell
   Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
   ```

5. Verify it works:

   ```powershell
   curl.exe localhost:8000/incidents
   ```

### Optional: run only Postgres in Docker

If you do not want to install Postgres directly, you can run only the database
container and still run the API on your machine:

```bash
docker compose up -d db
```

Then use the same local `DATABASE_URL` with `localhost`:

```ini
DATABASE_URL=postgresql+psycopg://incident:incident@localhost:5432/incidents
```

## Database & schema

Tables are created automatically on app startup via `Base.metadata.create_all`. This
is fine for early development, but note it **only creates missing tables — it does not
alter existing ones.** If you change a model after the table exists, either wipe the
volume (`docker compose down -v`) or adopt [Alembic](https://alembic.sqlalchemy.org/)
for migrations once you have data you can't throw away.

## Configuration

All configuration is via environment variables (see `.env.example`):

| Variable            | Purpose                                          |
| ------------------- | ------------------------------------------------ |
| `POSTGRES_USER`     | Postgres role name                               |
| `POSTGRES_PASSWORD` | Postgres password                                |
| `POSTGRES_DB`       | Database name                                    |
| `DATABASE_URL`      | SQLAlchemy connection string used by the API     |
