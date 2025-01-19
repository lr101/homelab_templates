# Homelab Templates

This repository contains setup templates and configuration files for various applications running in my home lab environment. It serves as a centralized location for maintaining and versioning infrastructure-as-code configurations.

## Applications

| Application | Description | Link |
|-------------|-------------|------|
| [MonaServer](https://github.com/lr101/MonaServer) | Backend server powering the Stick-It app | [/monaserver](./MonaServer) |
| Home Assistant | Open source home automation platform | [/homeassistant](./homeassistant) |
| Bitwarden | Self-hosted password manager | [/bitwarden](./bitwarden) |
| Nextcloud | Self-hosted file sync and collaboration platform | [/nextcloud](./nextcloud) |
| Portainer | Docker container management UI | [/portainer](./portainer) |
| Tempserver | Temperature monitoring and logging | [/tempserver](./tempserver) |
| Traefik-Thinkpad | Traefik reverse proxy | [/traefik-thinkpad](./traefik-thinkpad) |
| Logging | Influxdb, grafana, telegraf | [/logging](./logging) | 
| Homarr | Self-hosted dashboard | [/homarr](./homarr) | 


## Purpose

The goal of this repository is to:
- Maintain version control of configuration files
- Document setup procedures
- Enable quick recovery/redeployment of services
- Share configurations across different environments

## Getting Started

Each application folder contains the used setup (mostly docker-compose.yml) and the used configuration files with exempted secrets.
