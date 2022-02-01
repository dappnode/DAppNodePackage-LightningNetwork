#!/usr/bin/env bash
set -e

# Create restore symlink
if [ ! -L /rtl/backup/restore ]; then
  ln -s /rtl/backup /rtl/backup/restore
fi

# Configure settings from env vars
envsubst < "source_RTL-Config.json" > "RTL-Config.json"

envsubst < "source_RTL.conf" > "RTL.conf"

exec node rtl
