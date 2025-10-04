# How to Create a Backup

## Autorestic

I am using Autorestic to use the restic/rclone functionality to backup incremental snapshots.
See the [official docs](https://autorestic.vercel.app/config).

1. Install autorestic and rclone:
    ```shell
    # Autorestic
    wget -qO - https://raw.githubusercontent.com/cupcakearmy/autorestic/master/install.sh | bash

    # Rclone
    sudo -v ; curl https://rclone.org/install.sh | sudo bash
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
    ```
    sudo cp ~/.config/rclone/rclone.conf /root/rclone/rclone.conf
    sudo autorestic --ci backup -a
    ```

## Run as Cron

