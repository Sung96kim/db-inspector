# pg-inspector

PostgreSQL CLI visual inspector with a terminal UI (TUI). Connect to Postgres, browse schemas and tables, view data, and run SQL from the terminal.

**Requirements:** Python 3.13+, [uv](https://docs.astral.sh/uv/)

## Install

```bash
uv sync
```

## Run

Connection via `DATABASE_URL` or `-c` / `--connection`:

```bash
DATABASE_URL=postgres://user:pass@localhost:5432/mydb uv run pg-inspector
```

```bash
uv run pg-inspector -c "postgres://user:pass@localhost:5432/mydb"
```

Or as a module:

```bash
uv run python -m inspector -c "postgres://..."
```

No credentials in the repo; use env or CLI only.

## Docker

Start Postgres and run the inspector:

```bash
docker compose up -d postgres
docker compose run --rm -it pg-inspector
```

The compose `pg-inspector` service uses `DATABASE_URL=postgres://pguser:pgpass@postgres:5432/pgdb` by default. Override with `-e DATABASE_URL=...` or an `env_file` if needed.

Build the image:

```bash
docker compose build pg-inspector
```

## Postgres in Kubernetes

If the database is only reachable inside the cluster, port-forward then connect to localhost:

```bash
kubectl port-forward svc/postgres -n <namespace> 5432:5432
DATABASE_URL=postgres://user:pass@127.0.0.1:5432/mydb uv run pg-inspector
```

No Kubernetes-specific logic in the app.

## License

See [LICENSE](LICENSE).
