# Pi-Hole problems:

log files get to big:

Dont know the cause or long term fix but reduce log file size with this command:

```
sudo truncate -s100 /var/log/pihole/pihole_updateGravity.log
```
