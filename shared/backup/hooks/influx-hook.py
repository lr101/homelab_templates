#!/usr/bin/env python3
import os
import sys
import argparse
import json
import urllib.request
import urllib.error
from datetime import datetime

def load_env(path=".env"):
    """Simple .env loader using only the standard library."""
    # Resolve environment path: expand vars/user and treat relative paths as relative to this script
    path = os.path.expanduser(os.path.expandvars(path))
    if not os.path.isabs(path):
        script_dir = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(script_dir, path)
    if not os.path.exists(path):
        print(f"Warning: .env file not found at {path}")
        return

    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ[key.strip()] = value.strip()

def get_env_var(name):
    """Get environment variable or exit if missing."""
    value = os.getenv(name)
    if not value:
        print(f"Missing required environment variable: {name}")
        sys.exit(1)
    return value

def write_backup_status(host, service, success):
    """Send backup result to InfluxDB via HTTP API."""
    url = get_env_var("INFLUXDB_URL").rstrip("/")
    token = get_env_var("INFLUXDB_TOKEN")
    org = get_env_var("INFLUXDB_ORG")
    bucket = get_env_var("INFLUXDB_BUCKET")

    # Measurement: backup_status
    # Tags: host, service
    # Fields: status (int), status_text (string)
    status_text = "success" if success else "failure"
    status_value = 1 if success else 0

    # InfluxDB line protocol
    timestamp_ns = int(datetime.now().timestamp() * 1e9)
    line = f"backup_status,host={host},service={service} status={status_value}i,status_text=\"{status_text}\" {timestamp_ns}"

    api_url = f"{url}/api/v2/write?org={org}&bucket={bucket}&precision=ns"
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "text/plain; charset=utf-8",
    }

    req = urllib.request.Request(api_url, data=line.encode("utf-8"), headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req) as resp:
            if resp.status == 204:
                print(f"Wrote backup status for '{service}' on '{host}' ({status_text}).")
            else:
                print(f"Unexpected response: {resp.status}")
    except urllib.error.HTTPError as e:
        print(f"HTTPError: {e.code} - {e.reason}")
        try:
            err_body = e.read().decode()
            print("Response:", err_body)
        except Exception:
            pass
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"URLError: {e.reason}")
        sys.exit(1)

def parse_args():
    parser = argparse.ArgumentParser(description="Push backup status updates to InfluxDB.")
    parser.add_argument("--host", required=True, help="Hostname where the backup ran.")
    parser.add_argument("--service", required=True, help="Service or application name.")
    parser.add_argument("--status", required=True, choices=["success", "failure"], help="Backup result status.")
    parser.add_argument("--env-file", default=".env", help="Path to .env file (default: .env).")
    return parser.parse_args()

def main():
    args = parse_args()
    load_env(args.env_file)
    success = args.status.lower() == "success"
    write_backup_status(args.host, args.service, success)

if __name__ == "__main__":
    main()
