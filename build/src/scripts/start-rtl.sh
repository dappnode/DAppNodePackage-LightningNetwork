#!/usr/bin/env bash
set -e

# Create restore symlink
ln -s /rtl/backup /rtl/backup/restore

# Configure settings from env vars
envsubst < "source_RTL.conf" > "RTL.conf"

node rtl