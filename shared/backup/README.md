# Backup

This folder contains the deployment files and other utilise to easily setup backups for the different devices it is used on. The different services in the homelab_templates repository are already split by the hardware devices they are running on (for example the thinkpad or medion laptops). In every of these directories lies an ´autorestic.yml´ file which details the backup plan (keeping to the 3-2-1 rule). The [docker-compose.yml](./docker-compose.yml) file in this directory is the back-up software and configuration that then execute the backup plans. For this *autorestic* is used.

## Setup Autorestic

When adding a new device the following steps need to be taken:

1. Create a new folder in the root of this repo and create an `.autorestic.yml` file.
2. Add the backup plan. See [autorestic](https://autorestic.vercel.app/location) for more information.
3. Create a `.env` file in this directory, containing the path to the new location. For example:
    ```
    DEVICE_FOLDER_PATH=/home/lr/homelab_templates/thinkpad
    ```
4. Add the backend configurations. This depends on your setup:

- **SFTP**
  - Mount .ssh key folder: `~/.ssh:/root/.ssh:ro`
  - .autorestic.yml:
    ```yaml
    backends:
      <name>:
        type: sftp
        path: <host>:<path>
    ```

- **Rclone**
  - Mount rclone config: `./rclone.conf:/root/.config/rclone/:ro`
  - CLI Commands: Run the following to setup rclone:
    ```sh
    docker compose run --rm -v "$(pwd)":/rclone_config autorestic rclone config --config /rclone_config/rclone.conf
    ```
  - .autorestic.yml:
    ```yaml
    backends:
      <name>:
        type: rclone
        path: <remote>:<path>
    ```

- **Local**
  - Mount local backup dir: `~/backup:/backup`
  - .autorestic.yml:
    ```yaml
    backends:
      <name>:
        type: local
        path: /backup
    ``` 

5. Run 
```sh
sudo docker compose run --rm autorestic autorestic -c /data/.autorestic.yml check
```
This will check if your configuration is configured correctly, initializes the backends and generates the encryption keys. To commit the `.autorestic.yml` file to git, make sure to copy the generated keys into a `.autorestic.env` file next to it. Remomve the keys from the config and name the entries with the schema: `AUTORESTIC_<backend>_RESTIC_PASSWORD=...`.

6. Startup: `sudo docker compose up -d`

## Setup Hooks

The [hooks](./hooks/) contains useful scripts that are currently used by autorestic for backup purposes.

To use the [influx-hook.py](./influx-hook.py) script, a `.env` file needs to be created at [hooks/.env](./hooks/.env) with the following values:

```env
INFLUXDB_URL=https://influx.medion.lr-projects.de
INFLUXDB_TOKEN=<token>
INFLUXDB_BUCKET=restic_backup
INFLUXDB_ORG=lr-projects
```

## Restore:

Use the following to restore. If autorestic is already running `sudo docker container exec` can be used. Otherwise navigate to [shared/backup](./) and use `sudo docker compose run --rm`:
```sh
# List snapshot metadata
sudo docker container exec autorestic autorestic -c /data/.autorestic.yml exec -av -- snapshots

# Restore a specific snapshot
sudo docker container exec autorestic autorestic -c /data/.autorestic.yml restore -l <location> --from <backend> --to /data/<directory> <snapshot>

# Set correct access rights
sudo chown -R <user>:<user> $DEVICE_FOLDER_PATH/<directory>

# Move data to the correct directory
mv $DEVICE_FOLDER_PATH/<directory>/data/<location> /<some_location>
```

For example based on traefik running in the thinkpad folder:
```sh
sudo docker container exec autorestic autorestic -c /data/.autorestic.yml restore -l traefik --from nas --to /data/.restore f291f55a

sudo chown -R lr:lr ~/homelab_templates/thinkpad/.restore/

mv ~/homelab_templates/thinkpad/.restore/data/traefik ~/traefik-restored
```