#!/usr/bin/env bash
set -euo pipefail
umask 077

NETWORK=${NETWORK:-mainnet}
BITCOIND_HOST=${BITCOIND_HOST:-bitcoin.dappnode}
RPCUSER=${RPCUSER:-dappnode}
RPCPASS=${RPCPASS:-dappnode}
case "$NETWORK" in
  mainnet) default_rpcport=8332 ;;
  testnet) default_rpcport=18332 ;;
  signet) default_rpcport=38332 ;;
  regtest) default_rpcport=18443 ;;
  *) echo "Unsupported Bitcoin network: $NETWORK" >&2; exit 1 ;;
esac
BITCOIND_RPCPORT=${BITCOIND_RPCPORT:-$default_rpcport}

state=${HOME:-/root}/.lnd
marker=$state/.dappnode-lnd-0.21-ready
wallet=$state/data/chain/bitcoin/$NETWORK/wallet.db
if [[ -f $wallet && ! -f $marker && ${LND_MIGRATION_CONFIRMED:-false} != true ]]; then
  echo "Existing LND wallet requires the staged upgrade in MIGRATION.md. Set LND_MIGRATION_CONFIRMED=true only after completing it on a backed-up installation." >&2
  exit 1
fi
mkdir -p "$state" /shared
touch "$marker"

# LND generates its own TLS certificate and network-specific macaroon files.
# Never create a dangling admin.macaroon symlink or an unbacked seedless wallet.
args=(
  --bitcoin.active "--bitcoin.$NETWORK" --bitcoin.node=bitcoind
  "--bitcoind.rpchost=$BITCOIND_HOST:$BITCOIND_RPCPORT"
  "--bitcoind.rpcuser=$RPCUSER" "--bitcoind.rpcpass=$RPCPASS"
  --tlscertpath=/shared/tls.cert --tlskeypath=/root/.lnd/tls.key
  --adminmacaroonpath=/shared/admin.macaroon
  --tlsextradomain=lnd.lightning-network.dappnode --tlsextradomain=lnd
  --tlsautorefresh
  --restlisten=0.0.0.0:8080 "--debuglevel=${DEBUG:-info}"
  "--alias=${ALIAS:-Dappnode}" "--color=${COLOR:-#5ACDC5}"
)
if [[ ${BITCOIND_RPC_POLLING:-false} == true ]]; then
  args+=(--bitcoind.rpcpolling)
else
  args+=("--bitcoind.zmqpubrawblock=tcp://$BITCOIND_HOST:28332"
         "--bitcoind.zmqpubrawtx=tcp://$BITCOIND_HOST:28333")
fi
if [[ -n ${EXT_IP:-} ]]; then args+=("--externalip=$EXT_IP"); fi
exec lnd "${args[@]}" "$@"
