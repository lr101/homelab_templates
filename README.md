# Homelab Templates

This repository contains setup templates and configuration files for various applications running in my home lab environment. It serves as a centralized location for maintaining and versioning infrastructure-as-code configurations.

## Applications

| Application | Description | Link |
|-------------|-------------|------|
| [MonaServer](https://github.com/lr101/MonaServer) | Backend server powering the Stick-It app | [/monaserver](./monaserver) |
| Home Assistant | Open source home automation platform | [/homeassistant](./homeassistant) |

## Purpose

The goal of this repository is to:
- Maintain version control of configuration files
- Document setup procedures
- Enable quick recovery/redeployment of services
- Share configurations across different environments

## Getting Started

Each application folder contains the used setup (mostly docker-compose.yml) and the used configuration files with exempted secrets.
