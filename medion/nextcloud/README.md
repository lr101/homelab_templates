# Nextcloud setup

## SSO

Followed [this](https://pocket-id.org/docs/client-examples/nextcloud) tutorial for SSO setup. Group provisioning is done via groups:

- ?

Enable auto redirect to SSO:

```bash
docker exec --user www-data -it nextcloud-nextcloud-1 php occ config:app:set --value=0 user_oidc allow_multiple_user_backends
```
