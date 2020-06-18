#!/usr/bin/env bash
set -e

# Create restore dir
[ -d /rtl/backup/restore ] || [ -L /rtl/backup/restore ] || mkdir -p /rtl/backup/restore

# Configure settings from env vars
envsubst <"source_RTL.conf" >"RTL.conf"

node rtl
