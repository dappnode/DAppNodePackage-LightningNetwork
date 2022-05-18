#!/usr/bin/env bash
set -e

# Configure settings from env vars
envsubst < "source_RTL.conf" > "RTL.conf"

node rtl