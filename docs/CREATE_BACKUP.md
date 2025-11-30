# How to Create a Backup

## Autorestic

I am using Autorestic to use the restic/rclone functionality to backup incremental snapshots.
See the [official docs](https://autorestic.vercel.app/config).

### Privileges

There are multiple ways on how to handle privileges in which your backup is running. The problem is that many applications you want to backup have files with higher privileges than the default user. A backup on these files can therefore only be performed with sufficient permissions. These are your options:

1. Run as a normal non-root user
2. Run as root
3. Run using a specific user with read only access to all files. See this [restic](https://restic.readthedocs.io/en/latest/080_examples.html#backing-up-your-system-without-running-restic-as-root) example.

After deciding, switch to your user for all of the next steps (especially for crontab):
```
su - <user>
```

### Setup Google Drive Rclone (optional)

This guide presents on how to setup Google Drive as a backup target location using rclone. See [rclone docs](https://rclone.org/docs/) for other providers.

1. Prepare your google account project
   1. Create a google project under the [google cloud dashboard](https://console.cloud.google.com/apis/dashboard) -> New Project
   2. On the same page click on "Activate APIs and Services" at the top -> Select Google Drive -> Activate
   3. On the sidebar select "OAuth Consent Screen" -> Clients -> Go to the setup guide to activate the Google Oauth Platform
   4. Under the Clients tab -> Create a new OAuth Client -> Give it a name and store the shown client-id and secret
   5. Open the "OAuth Consent Screen (Zielgruppe)" -> Testuser -> Add the gmail used in the OAuth Client to the test user group (See [here](https://stackoverflow.com/questions/75454425/access-blocked-project-has-not-completed-the-google-verification-process for more info))
2. Install rclone: `sudo -v ; curl https://rclone.org/install.sh | sudo bash`
3. Create a new config: `rclone config`
4. Go through the setup process of rclone by using the created client-id and secret.

**Note**: Make sure your rclone config is under the same user home (~/.config/rclone/rclone.conf) as your autorestic installation.

### Setup autorestic

1. Install autorestic and rclone:
```shell
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
```shell
autorestic --ci backup -a
```

## Run as Cron

Currenty I just do something like this and running it directly in cron:

```shell
crontab -e

# Copy the next two lines and adjust the folder path
PATH="/usr/local/bin:/usr/bin:/bin"    # This is required, as it otherwise cannot find restic as a command.
0 2 * * *  autorestic -c <path>/.autorestic.yml --ci backup -a # Adjust the path to your config file
```
