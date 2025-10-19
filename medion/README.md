# Deployments

Device: Medion

## Configs

I sometimes had problems on this device to get DNS working correctly:

1. When rebooting wireguards DNS config in `/etc/resolve.conf` gets overwritten. Therefore restarting wireguard needs to be done manually.

2. Docker containers sometimes do not use the correct DNS server. This can be fixed by setting them in the `/etc/docker/daemon.json`:

```json
{
    "dns": [
        "10.217.236.1",
        "8.8.8.8",
        "8.8.4.4"
    ],
    "runtimes": {
        "nvidia": {
            "args": [],
            "path": "nvidia-container-runtime"
        }
    }
}
```
