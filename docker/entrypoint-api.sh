#!/bin/sh
set -e

echo "Waiting for Postgres..."
python - <<'PY'
import os, time
import psycopg

host = os.environ.get("POSTGRES_HOST", "db")
port = int(os.environ.get("POSTGRES_PORT", "5432"))
user = os.environ.get("POSTGRES_USER", "evacode")
password = os.environ.get("POSTGRES_PASSWORD", "evacode")
dbname = os.environ.get("POSTGRES_DB", "evacode_crm")

for i in range(60):
    try:
        with psycopg.connect(
            host=host, port=port, user=user, password=password, dbname=dbname
        ) as conn:
            conn.execute("SELECT 1")
        print("Postgres is up")
        break
    except Exception as e:
        print(f"Postgres not ready ({e}), retry {i+1}/60")
        time.sleep(1)
else:
    raise SystemExit("Postgres did not become ready")
PY

python manage.py migrate --noinput
python manage.py seed_demo
exec "$@"
