#!/bin/sh
# cron-entrypoint.sh

if [ "$1" = cron ]; then
  ./api/manage.py crontab remove
  ./api/manage.py crontab add
fi

# Launch the main container command passed as arguments.
exec "$@"

