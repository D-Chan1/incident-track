# incident-track

A FastAPI service backed by PostgreSQL for tracking incidents, with a Reddit RSS scraper.

## Stack

- **API:** FastAPI + Uvicorn
- **Database:** PostgreSQL 17, accessed via SQLAlchemy 2.0 (`psycopg` driver)
- **Containerization:** Docker Compose (app + database)

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) with Compose v2 (`docker compose`)
- That's it for the Docker workflow. To run the API directly on your machine, you'll also need Python 3.12.

## Quick start (Docker)

1. **Create your environment file** from the template:

   ```bash
   cp .env.example .env
   ```

   The defaults work out of the box for local development:

   ```ini
   POSTGRES_USER=incident
   POSTGRES_PASSWORD=incident
   POSTGRES_DB=incidents
   DATABASE_URL=postgresql+psycopg://incident:incident@db:5432/incidents
   ```

   > The `DATABASE_URL` host is `db` (the Compose service name), not `localhost` —
   > inside the Docker network the app reaches Postgres by service name.

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

## Running the API without Docker

Useful for fast iteration. You still need a Postgres instance — the simplest path is
to run just the database in Docker and the API on your host.

1. Start only the database:

   ```bash
   docker compose up -d db
   ```

2. Install dependencies and run the API, pointing at the **published** port on
   `localhost`:

   ```bash
   pip install -r requirements.txt
   DATABASE_URL=postgresql+psycopg://incident:incident@localhost:5432/incidents \
     uvicorn backend.main:app --reload
   ```

   (`localhost` here, not `db`, because the app is now running on your machine and
   reaching Postgres through the published port.)

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

`.env` is gitignored — never commit real credentials.
