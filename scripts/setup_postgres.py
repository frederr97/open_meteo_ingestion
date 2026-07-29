#!/usr/bin/env python3
"""Apply SQL bootstrap files to create PostgreSQL structures."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
import psycopg2

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def main() -> int:
    sql_dir = Path(__file__).resolve().parent.parent / "database" / "sql"
    sql_files = sorted(sql_dir.glob("*.sql"))

    if os.getenv("DRY_RUN") == "1":
        print("Dry run enabled. SQL files to be applied:")
        for sql_path in sql_files:
            print(f"- {sql_path}")
        return 0

    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        dbname=os.getenv("POSTGRES_DATABASE"),
        user=os.getenv("POSTGRES_USERNAME"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )

    with conn:
        with conn.cursor() as cursor:
            for sql_path in sql_files:
                print(f"Applying {sql_path.name}...")
                cursor.execute(sql_path.read_text(encoding="utf-8"))

    print("Database bootstrap completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
