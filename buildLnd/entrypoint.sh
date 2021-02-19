#!/bin/sh

set -e

# Set default alias if does not exist
if [ -z ${ALIAS} ] 
then
  echo "setting default alias: dappnode"
  UI_PASSWORD="dappnode"
else
  echo "setting alias"
fi

if [ -z ${MAINNET} ] 
then
  echo "setting default mainnet: false"
  MAINNET="false"
else
  echo "setting mainnet: ${MAINNET}"
fi

cat > /root/.lnd/lnd.conf <<EOF
[Application Options]
datadir=/root/.lnd/data
logdir=/root/.lnd/logs
maxlogfiles=3
maxlogfilesize=10
tlscertpath=/shared/tls.cert
tlskeypath=/root/.lnd/tls.key
letsencryptdir=/root/.lnd/letsencrypt
adminmacaroonpath=/shared/admin.macaroon
readonlymacaroonpath=/root/.lnd/data/chain/bitcoin/mainnet/readonly.macaroon
invoicemacaroonpath=/root/.lnd/data/chain/bitcoin/mainnet/invoice.macaroon
listen=0.0.0.0:9735
rpclisten=0.0.0.0:10009
restlisten=0.0.0.0:8080
debuglevel=debug,PEER=info
maxpendingchannels=10
backupfilepath=/shared/channel.backup
alias=${ALIAS}

[Bitcoin]
bitcoin.active=true
bitcoin.chaindir=/root/.lnd/data/chain/bitcoin
bitcoin.mainnet=${MAINNET}
bitcoin.node=bitcoind

[bitcoind]
bitcoind.dir=/root/.bitcoin
bitcoind.rpchost=bitcoin.dnp.dappnode.eth
bitcoind.rpcuser=dappnode
bitcoind.rpcpass=dappnode
bitcoind.zmqpubrawblock=tcp://bitcoin.dnp.dappnode.eth:28332
bitcoind.zmqpubrawtx=tcp://bitcoin.dnp.dappnode.eth:28333

[Autopilot]
autopilot.active=true
EOF

lnd