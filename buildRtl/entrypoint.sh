#!/bin/sh

set -e

# Set default UI password if does not exist
if [ -z ${UI_PASSWORD} ] 
then
  echo "setting default UI password: dappnode"
  UI_PASSWORD="dappnode"
else
  echo "setting UI password"
fi

cat > /RTL/RTL-Config.json <<EOF
{
  "multiPass": "$UI_PASSWORD",
  "port": "80",
  "host": "0.0.0.0",
  "SSO": {
    "rtlSSO": 0
  },
  "nodes": [
    {
      "index": 1,
      "lnNode": "Node 1",
      "lnImplementation": "LND",
      "Authentication": {
        "macaroonPath": "/shared"
      },
      "Settings": {
        "userPersona": "MERCHANT",
        "themeMode": "NIGHT",
        "themeColor": "PURPLE",
        "channelBackupPath": "/shared/lnd/backup",
        "enableLogging": "true",
        "fiatConversion": "true",
        "currencyUnit": "USD",
        "lnServerUrl": "https://lnd.lightning-network.public.dappnode:8080"
      }
    }
  ]
}
EOF

node rtl