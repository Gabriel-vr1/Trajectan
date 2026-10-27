"""Run once as the private-network Container Apps bootstrap job.
Credentials arrive only through Container Apps secrets. Never print connection URLs.
"""

import os
import psycopg
from psycopg import sql
from sqlalchemy.engine import make_url


def main():
    url = make_url(os.environ["DATABASE_ADMIN_URL"])
    password = os.environ["APP_DATABASE_PASSWORD"]
    with psycopg.connect(
        host=url.host,
        port=url.port or 5432,
        dbname=url.database,
        user=url.username,
        password=url.password,
        sslmode="require",
    ) as db:
        role = "trajectanapp"
        exists = db.execute(
            "SELECT 1 FROM pg_roles WHERE rolname = %s", (role,)
        ).fetchone()
        if not exists:
            db.execute(
                sql.SQL(
                    "CREATE ROLE {} LOGIN PASSWORD {} NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION"
                ).format(sql.Identifier(role), sql.Literal(password))
            )
        else:
            db.execute(
                sql.SQL(
                    "ALTER ROLE {} PASSWORD {} NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION"
                ).format(sql.Identifier(role), sql.Literal(password))
            )
        db.execute(
            sql.SQL("GRANT CONNECT ON DATABASE {} TO {}").format(
                sql.Identifier(url.database), sql.Identifier(role)
            )
        )
        db.execute("REVOKE CREATE ON SCHEMA public FROM PUBLIC")
        db.execute(
            sql.SQL("GRANT USAGE, CREATE ON SCHEMA public TO {}").format(
                sql.Identifier(role)
            )
        )
    print(
        "Application database role prepared; administrative credentials are not used by the API."
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        # Driver errors can contain sensitive connection details.
        raise SystemExit("Database bootstrap failed: " + type(error).__name__) from None
