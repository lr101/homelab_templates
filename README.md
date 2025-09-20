# Homelab Templates

This repository contains setup templates and configuration files for various applications running in my home lab environment. It serves as a centralized location for maintaining and versioning infrastructure-as-code configurations.

## Applications

### Thinkpad

| Name          | Description                          | Device   | Domain                  | Backup Solution | Update Solution | SSO Integration |
|---------------|--------------------------------------|----------|-------------------------|-----------------|-----------------|------------------|
| Bitwarden     | Password manager                    | Thinkpad | bitwarden.lr-projects.de | ✅              | `cron`              | must be standalone |
| Diun          | Docker image update notifier        | Thinkpad | -      |  -             | `manual`              | - |
| Watchtower    | Docker image updater        | Thinkpad | -      | -              | `manual`              | - |
| Glance        | System monitoring dashboard         | Thinkpad | home.lr-projects.de    | -               | `watchtower :latest`              | - |
| Home Assistant| Home automation platform            | Thinkpad | ha.thinkpad.lr-projects.de | -          | `watchtower :stable`              | ✅ |
| InfluxDB      | Time-series database                | Thinkpad | influx.thinkpad.lr-projects.de  | ❌ (dont really need) | `watchtower :2.6-ubuntu`    | ❌ (community edition not possible)|
| Grafana      | Alerting and montoring of metric data                | Thinkpad | grafana.thinkpad.lr-projects.de  | ❌ (manually in this repo)             | `watchtower :latest` | ✅ | 
| Telegraf      | Metric collector                | Thinkpad | -  | -              | `watchtower :1.31-alpine`                 | - |
| Nextcloud     | File sharing and collaboration      | Thinkpad | nextcloud.lr-projects.de | ✅              | `watchtower :latest`               | ✅ |
| Nextcloud (MariaDB)     | Nextcloud database      | Thinkpad | - | -              | `watchtower :lts`               | - |
| Nextcloud (Redis)     | Nextcloud in-memory db      | Thinkpad | - | -              | `watchtower :latest`               | - |
| Monaserver       | Stick It backend                 | Thinkpad | stick-it.lr-projects.de   | ✅              | `manual`              | - |
| Monaserver (Postgis)      | Stick It postgis database                 | Thinkpad | -   | ✅              | `manual`              | - |
| Monaserver (Minio)      | Stick It image bucket                 | Thinkpad | minio.thinkpad.lr-projects.de   | ✅              | `manual`              | ❌ (community edition not possible) |
| Traefik      | Reverse Proxy (with https)                 | Thinkpad | traefik.thinkpad.lr-projects.de   | -              | `watchtower :v3` | ✅  |
| Portfolio      | Homepage of lr-projects                 | Thinkpad | lr-projects.de   | -              | `manual` | - |
| Stick-It Homepage      | Landing page of the Stick-It app| Thinkpad | stick-it-map.lr-projects.de   | -              | `manual` | - |


### Medion

| Name          | Description                          | Device   | Domain                  | Backup Solution | Update Solution | SSO Integration |
|---------------|--------------------------------------|----------|-------------------------|-----------------|-----------------|-----------------|
| Immich           | Image storage | Medion | immich.medion.lr-projects.de |  ❌             | ``              | ✅ |
| Jellyfin         | Movie storage | Medion | jellyfin.medion.lr-projects.de      |  ❌             |               | ✅ |
| Pocket-ID        | SSO solution         | Medion | sso.medion.lr-projects.de      |  ❌             |               | ✅ |
| Pi-Hole          | DNS for home network         | Medion | pihole.medion.lr-projects.de      |  ❌             |               | ? |
| Traefik      | Reverse Proxy (with https)                 | Medion | traefik.medion.lr-projects.de   | -              |  | ✅ |
| Diun          | Docker image update notifier        | Medion | -      |  -             | `manual`              | - |
| Telegraf      | Metric collector                | Medion | -  | -              |                 | - |


### Ionos

| Name          | Description                          | Device   | Domain                  | Backup Solution | Update Solution | SSO Integration |
|---------------|--------------------------------------|----------|-------------------------|-----------------|-----------------|-----------------|
| Nginx-UI      | Reverse proxy (facing the internet)           | Ionos | nginx-ui.ionos.lr-projects.de |  ❌ (manually in this repo)            | ``              | ? |
| Pi-Hole       | DNS for vpn network         | Ionos | pi-hole.ionos.lr-projects.de      |  ❌             |               | ? |
| Telegraf      | Metric collector                | Ionos | -  | -              |                 | - |

## Homelab setup

A wireguard server, running on a very cheap VPS with a public IP, is used to connect all devices in the homelab.
This allows for (reverse) proxying of services running on the homelab to VPN clients. 
This also allows for the nginx proxy, running on the public VPS, to expose specific services to the internet.

![image](./images/setup.png)


## Purpose

The goal of this repository is to:
- Maintain version control of configuration files
- Document setup procedures
- Enable quick recovery/redeployment of services
- Share configurations across different environments

## Getting Started

Each application folder contains the used setup (mostly docker-compose.yml) and the used configuration files with exempted secrets.
