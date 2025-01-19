# Traefik on Thinkpad

## Setup

1. Go to Cloudflare dashboard and create a new API token with the following permissions: DNS, Zone, Read.
2. Add to .env file:
3. Run docker compose up -d

## Configuration of containers

Typical labels:
```
services:
  <NAME>:
    networks:
      - frontend
    labels:
      - traefik.enable=true
      - traefik.http.routers.<NAME>.rule=Host(`<SUBDOMAIN>.thinkpad.lr-projects.de`)
      - traefik.http.routers.<NAME>.entrypoints=websecure
      - traefik.http.routers.<NAME>.tls=true
      - traefik.http.routers.<NAME>.tls.certresolver=cloudflare
      - traefik.http.routers.<NAME>.service=<NAME>@internal
      - traefik.http.services.<NAME>@internal.loadbalancer.server.port=<PORT>

networks:
  frontend:
    external: true
```

## Notes
- Behind nginx dont use `set_proxy_headers host $HOST`as this will disrupt proxy in treafik