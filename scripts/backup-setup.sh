#!/bin/bash

# --- Check for Root ---
if [ "$EUID" -ne 0 ]; then
  echo "Error: Please run as root (sudo)."
  exit 1
fi

# --- Path Logic ---
# Script is in ./scripts/setup.sh, REPO_ROOT is one level up
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=========================================="
echo "   Autorestic System-Wide Backup Setup"
echo "=========================================="

# 1. Ask for Configurations with Defaults
DEFAULT_DEVICE="thinkpad"
read -p "Enter the folder path to the .autorestic.yml file [Default: $DEFAULT_DEVICE]: " DEVICE_NAME
DEVICE_NAME=${DEVICE_NAME:-$DEFAULT_DEVICE}

DEFAULT_CRON="10 2 * * *"
read -p "Enter cron schedule [Default: '$DEFAULT_CRON']: " CRON_INPUT
CRON_SCHEDULE=${CRON_INPUT:-$DEFAULT_CRON}

# Set Paths
DEVICE_CONFIG_DIR="$REPO_ROOT/$DEVICE_NAME"
AUTORESTIC_CONFIG="$DEVICE_CONFIG_DIR/.autorestic.yml"
LOG_DIR="/var/log/autorestic"
USER_HOME="/home/autorestic"
USER_BIN="$USER_HOME/bin"

# Validate that the config file actually exists
if [ ! -f "$AUTORESTIC_CONFIG" ]; then
    echo "Error: Config file not found at $AUTORESTIC_CONFIG"
    exit 1
fi

# 2. Create dedicated user
if id "autorestic" &>/dev/null; then
    echo "[!] User 'autorestic' already exists."
else
    echo "[+] Creating 'autorestic' system user..."
    useradd --system --create-home --shell /sbin/nologin autorestic
fi

# 3. Install Dependencies
apt-get update -y && apt-get install -y rclone curl wget libcap2-bin bzip2

# 4. Install Binaries to User Home
echo "[+] Installing binaries to $USER_BIN..."
mkdir -p "$USER_BIN"

# Install Restic
LATEST_RESTIC=$(curl -s https://api.github.com/repos/restic/restic/releases/latest | grep tag_name | cut -d '"' -f 4 | sed 's/v//')
wget -q "https://github.com/restic/restic/releases/download/v${LATEST_RESTIC}/restic_${LATEST_RESTIC}_linux_amd64.bz2" -O "$USER_BIN/restic.bz2"
bunzip2 -f "$USER_BIN/restic.bz2"
chmod +x "$USER_BIN/restic"

# Install Autorestic
curl -s https://raw.githubusercontent.com/cupcakearmy/autorestic/master/install.sh | INSTALL_PATH="$USER_BIN" bash

# 5. Restrict Permissions and Assign Capabilities
echo "[+] Assigning capabilities for non-root system access..."
chown root:autorestic "$USER_BIN/restic" "$USER_BIN/autorestic"
chmod 750 "$USER_BIN/restic" "$USER_BIN/autorestic"

# Grant permission to read all files without being root
setcap cap_dac_read_search=+ep "$USER_BIN/restic"
setcap cap_dac_read_search=pie "$USER_BIN/autorestic"

# 6. Rclone Configuration
read -p "Configure Rclone for 'autorestic' user now? (y/n): " RUN_RCLONE
if [[ $RUN_RCLONE == [yY] ]]; then
    sudo -u autorestic rclone config
fi

# 7. Permissions and Logging
mkdir -p "$LOG_DIR"
chown autorestic:autorestic "$LOG_DIR"
chown -R autorestic:autorestic "$DEVICE_CONFIG_DIR"

# 8. Setup Cron Job with Explicit PATH
echo "[+] Setting up crontab with secure PATH..."

# We define the PATH at the top of the crontab and then the command
CRON_PATH="PATH=/usr/local/bin:/usr/bin:/bin:$USER_BIN"
CRON_COMMAND="$USER_BIN/autorestic -c $AUTORESTIC_CONFIG backup -a >> $LOG_DIR/backup.log 2>&1"

# Assemble the new crontab:
# 1. Take existing crontab (excluding our current config to prevent duplicates)
# 2. Add the PATH definition
# 3. Add the new cron schedule
(
  crontab -u autorestic -l 2>/dev/null | grep -v "$AUTORESTIC_CONFIG" | grep -v "PATH="
  echo "$CRON_PATH"
  echo "$CRON_SCHEDULE $CRON_COMMAND"
) | crontab -u autorestic -

echo "=========================================="
echo "         Setup Successfully Completed"
echo "=========================================="
echo "Run this to verify your setup:"
echo "sudo -u autorestic autorestic -c $AUTORESTIC_CONFIG check"