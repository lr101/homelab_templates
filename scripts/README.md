# Scripts

This folder contains useful scripts that are currently used by autorestic for backup purposes.

To use the [influx-hook.py](./influx-hook.py) script, a `.env` file needs to be created in this directory with the following values:

```env
INFLUXDB_URL=https://influx.medion.lr-projects.de
INFLUXDB_TOKEN=<token>
INFLUXDB_BUCKET=restic_backup
INFLUXDB_ORG=lr-projects
```