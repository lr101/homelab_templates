FROM cupcakearmy/autorestic:latest

# Install dependencies
# dcron is the cron daemon for Alpine
RUN apk add --no-cache python3 py3-pip docker-cli rclone dcron


# Set default Environment Variables
ENV CRON_SCHEDULE="10 2 * * *"
ENV AUTORESTIC_CONFIG="/data/.autorestic.yml"

# Create the startup script
RUN echo '#!/bin/sh' > /entrypoint.sh && \
    echo 'echo "SHELL=/bin/bash" > /etc/crontabs/root' >> /entrypoint.sh && \
    echo 'echo "PATH=/usr/local/bin:/usr/bin:/bin" >> /etc/crontabs/root' >> /entrypoint.sh && \
    echo 'echo "$CRON_SCHEDULE autorestic backup -c $AUTORESTIC_CONFIG -a >> /var/log/autorestic/backup.log 2>&1" >> /etc/crontabs/root' >> /entrypoint.sh && \
    echo 'echo "Starting cron with schedule: $CRON_SCHEDULE"' >> /entrypoint.sh && \
    echo 'crond -f -l 2' >> /entrypoint.sh && \
    chmod +x /entrypoint.sh

# Run the script
CMD ["/entrypoint.sh"]