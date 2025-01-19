# Nextcloud

## Crontab tasks

Its better to set the tasks at system level and not inside the docker container (made problems for me):

```shell
crontab -e
```
with value:
```
*/5 * * * * docker exec -u www-data <container_name> php /var/www/html/cron.php
```

## Setup

It is for the best to follow the official setup steps. The `config.php` file in this folder can be used for reference how to configure mail and trusted domain. In the container it can be found under `/var/www/html/config/config.php`.