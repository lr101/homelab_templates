#!/usr/bin/env python3
"""postgres-restore.py

Restore Postgres dump files into a running Docker container.

Usage: postgres-restore.py CONTAINER PG_USER DUMP1 [DUMP2 ...] [--backup-dir DIR] [--create-db]

Each DUMP may be an absolute path or a filename located inside --backup-dir.
If a target DB name is not supplied, the script will try to infer it from the filename
by removing a leading '<container>-' prefix and stripping extensions/timestamps.
"""

from __future__ import annotations

import argparse
import gzip
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Restore Postgres dump files into a Docker container")
    p.add_argument("container", help="Docker container name or id running Postgres")
    p.add_argument("pg_user", help="Postgres user to run pg_restore as")
    p.add_argument("dump", help="Dump filename or path to restore")
    p.add_argument("db", help="Target database name to restore into")
    p.add_argument("--backup-dir", default=str(Path.cwd() / "postgres-backups"), help="Directory to find dumps in when a relative name is given")
    p.add_argument("--create-db", action="store_true", help="Create the target database before restoring if it does not exist")
    p.add_argument("--no-owner", action="store_true", help="Pass --no-owner to pg_restore (recommended when restoring to different server)")
    return p.parse_args()


def check_docker_present() -> None:
    if shutil.which("docker") is None:
        print("ERROR: docker CLI not found in PATH", file=sys.stderr)
        sys.exit(2)


def container_running(container: str) -> bool:
    try:
        out = subprocess.check_output(["docker", "ps", "--format", "{{.Names}}"], text=True)
        if any(line.strip() == container for line in out.splitlines()):
            return True
        out = subprocess.check_output(["docker", "ps", "--format", "{{.ID}}"], text=True)
        if any(line.strip() == container for line in out.splitlines()):
            return True
    except subprocess.CalledProcessError:
        pass
    return False


def db_exists(container: str, pg_user: str, db: str) -> bool:
    cmd = ["docker", "exec", container, "psql", "-U", pg_user, "-tAc", f"SELECT 1 FROM pg_database WHERE datname='{db}'"]
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True).strip()
        return out == "1"
    except subprocess.CalledProcessError:
        return False


def create_db(container: str, pg_user: str, db: str) -> bool:
    cmd = ["docker", "exec", container, "psql", "-U", pg_user, "-c", f"CREATE DATABASE \"{db}\";"]
    try:
        subprocess.check_call(cmd)
        return True
    except subprocess.CalledProcessError:
        return False


def run_pg_restore(container: str, pg_user: str, db: str, dump_path: Path, no_owner: bool) -> int:
    # Build pg_restore command executed inside container, read dump via stdin
    pg_restore_cmd = ["pg_restore", "-U", pg_user, "-d", db, "--clean"]
    if no_owner:
        pg_restore_cmd.append("--no-owner")

    docker_cmd = ["docker", "exec", "-i", container] + pg_restore_cmd

    print(f"Running: {' '.join(shlex.quote(c) for c in docker_cmd)} < {dump_path}")

    # open dump file (support gzip)
    open_func = gzip.open if dump_path.suffix == ".gz" or dump_path.name.endswith(".sql.gz") else open

    try:
        with open_func(dump_path, "rb") as f:
            proc = subprocess.Popen(docker_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            try:
                # stream file to stdin of pg_restore
                for chunk in iter(lambda: f.read(8192), b""):
                    proc.stdin.write(chunk)
                proc.stdin.close()
            except BrokenPipeError:
                # pg_restore closed stdin (likely error)
                pass
            out, err = proc.communicate()
            if proc.returncode != 0:
                if out:
                    print(out.decode(errors="replace"), file=sys.stderr)
                if err:
                    print(err.decode(errors="replace"), file=sys.stderr)
                return proc.returncode
    except FileNotFoundError:
        print(f"ERROR: dump file not found: {dump_path}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"ERROR: unexpected error while restoring {dump_path}: {e}", file=sys.stderr)
        return 5

    print(f"Success: restored {dump_path} -> {db}")
    return 0


def main() -> int:
    args = parse_args()

    check_docker_present()

    if not container_running(args.container):
        print(f"ERROR: container '{args.container}' is not running (by name or id)", file=sys.stderr)
        return 3

    backup_dir = Path(args.backup_dir)

    exit_code = 0

    dump_path = Path(args.dump)
    if not dump_path.is_absolute():
        dump_path = backup_dir / dump_path

    if not dump_path.exists() and exit_code == 0:
        print(f"ERROR: dump not found: {dump_path}", file=sys.stderr)
        exit_code = 4

    # infer db name
    dbname = args.db
    if not dbname and exit_code == 0:
        print(f"ERROR: could not infer target database name from '{dump_path.name}'; specify a file named '<container>-<dbname>[...].dump'", file=sys.stderr)
        exit_code = 5

    if not db_exists(args.container, args.pg_user, dbname) and exit_code == 0:
        if args.create_db:
            print(f"Database '{dbname}' does not exist; creating...")
            if not create_db(args.container, args.pg_user, dbname):
                print(f"ERROR: failed to create database '{dbname}'", file=sys.stderr)
                exit_code = 6
        else:
            print(f"ERROR: target database '{dbname}' does not exist. Rerun with --create-db to create it automatically.", file=sys.stderr)
            exit_code = 7

    if exit_code == 0:
        exit_code = run_pg_restore(args.container, args.pg_user, dbname, dump_path, args.no_owner)

    if exit_code == 0:
        print("All restores completed successfully")
    else:
        print(f"Completed with errors (exit {exit_code})", file=sys.stderr)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
