#!/usr/bin/env python3
import subprocess
import shlex
from pathlib import Path
import datetime
import sys
import argparse

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Create pg_dump backups from a Docker Postgres container")
    p.add_argument("nc_container", help="Docker container name or id running Nextcloud")
    p.add_argument("mysql_container", help="Docker container name or id running MySQL/MariaDB")
    p.add_argument("env_fi", help="MySQL user")
    p.add_argument("mysql_db", help="MySQL database name")
    p.add_argument("--backup-dir", default=str(Path.cwd() / "nextcloud-backups"), help="Directory to write backups to")
    return p.parse_args()

def run_cmd(cmd, **kwargs):
    """Run a shell command with error checking."""
    print(f"[CMD] {' '.join(shlex.quote(c) for c in cmd)}")
    result = subprocess.run(cmd, **kwargs)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")
    return result


def backup_nextcloud(
    nextcloud_container: str,
    mysql_container: str,
    mysql_user: str,
    mysql_password: str,
    mysql_db: str,
    backup_dir: Path,
):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = backup_dir / f"nextcloud_backup_{timestamp}"
    html_dir = out_dir / "html"
    db_dir = out_dir / "db"

    out_dir.mkdir(parents=True, exist_ok=True)
    db_dir.mkdir(parents=True, exist_ok=True)

    print("[INFO] Enabling Nextcloud maintenance mode...")
    run_cmd([
        "docker", "exec", nextcloud_container,
        "php", "/var/www/html/occ", "maintenance:mode", "--on"
    ])

    print("[INFO] Copying Nextcloud html directory...")
    run_cmd([
        "docker", "cp",
        f"{nextcloud_container}:/var/www/html",
        str(html_dir)
    ])

    print("[INFO] Dumping database...")
    db_backup_path = db_dir / f"{mysql_db}.sql"
    with open(db_backup_path, "wb") as f:
        proc = subprocess.Popen([
            "docker", "exec", mysql_container,
            "mysqldump", "--single-transaction",
            "-h", "localhost",
            "-u", mysql_user,
            f"-p{mysql_password}",
            mysql_db
        ], stdout=f)
        proc.wait()
        if proc.returncode != 0:
            raise RuntimeError("mysqldump failed")

    print("[INFO] Disabling Nextcloud maintenance mode...")
    run_cmd([
        "docker", "exec", nextcloud_container,
        "php", "/var/www/html/occ", "maintenance:mode", "--off"
    ])

    print(f"[SUCCESS] Backup complete at: {out_dir}")


if __name__ == "__main__":
    args = parse_args()

    nextcloud_container = args.nc_container
    mysql_container = args.mysql_container
    mysql_user = args.mysql_user
    mysql_password = args.mysql_password
    mysql_db = args.mysql_db
    backup_dir = Path(args.backup_dir)

    backup_nextcloud(
        nextcloud_container,
        mysql_container,
        mysql_user,
        mysql_password,
        mysql_db,
        backup_dir
    )
