# How to Create a Backup

## Autorestic

I am using Autorestic to use the restic/rclone functionality to backup incremental snapshots.
See the [official docs](https://autorestic.vercel.app/config).

### Setup Google Drive Rclone (optional)

This guide presents on how to setup Google Drive as a backup target location using rclone. See [rclone docs](https://rclone.org/docs/) for other providers.

1. Prepare your google account project
   1. Create a google project under the [google cloud dashboard](https://console.cloud.google.com/apis/dashboard) -> New Project
   2. On the same page click on "Activate APIs and Services" at the top -> Select Google Drive -> Activate
   3. On the sidebar select "OAuth Consent Screen" -> Clients -> Go to the setup guide to activate the Google Oauth Platform
   4. Under the Clients tab -> Create a new OAuth Client -> Give it a name and store the shown client-id and secret
   5. Open the "OAuth Consent Screen (Zielgruppe)" -> Testuser -> Add the gmail used in the OAuth Client to the testuser group (See [here](https://stackoverflow.com/questions/75454425/access-blocked-project-has-not-completed-the-google-verification-process for more info))
2. Install rclone: `sudo -v ; curl https://rclone.org/install.sh | sudo bash`
3. Create a new config: `rclone config`
4. Go through the setup process of rclone by using the created client-id and secret.
5. (Optional) Copy config to root user:
```shell
cd ~
sudo cp -r .config/rclone/ /root/.config
```

### Setup autorestic

1. Install autorestic and rclone:
    ```shell
    # Autorestic
    wget -qO - https://raw.githubusercontent.com/cupcakearmy/autorestic/master/install.sh | bash
    ```
    - When using a resitc repository, create it like [here](https://rclone.org/docs/). It can be used via `type: restic`

2. Create a `.autorestic.yml`

3. Check the config by running:
    ```shell
    autorestic check
    ```

4. Copy the generated key into a `.autorestic.env` file. The variable should have the name `AUTORESTIC_[backend-name]_RESTIC_PASSWORD`.

5. In the current version 1.8.3 there is a bug that generates a faulty entry called `forgetoption`. Just remove it everywhere in your autorestic config.

6. Run your backup:
    - As non-root:
    ```shell
    autorestic --ci backup -a
    ```
    - As root: You first need to copy your rclone config into the root users home. Something like:
    ```shell
    # If using rclone, make sure the config is in the root users directory
    sudo autorestic --ci backup -a
    ```

## Run as Cron

Currenty I just do something like this and running it directly in cron:

```shell
sudo crontab -e

# Copy and adjust the folder path
0 2 * * *  autorestic -c /home/lr/homelab_templates/medion/.autorestic.yml --ci backup -a
```