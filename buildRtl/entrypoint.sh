#!/bin/sh
set -eu
umask 077
node /opt/dappnode/render-config.cjs
cd /RTL
exec node rtl.js
