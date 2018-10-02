#!/usr/bin/env bash

# exit from script if error was raised.
set -e

# error function is used within a bash function in order to send the error
# message directly to the stderr output and exit.
error() {
    echo "$1" > /dev/stderr
    exit 0
}

# return is used within bash function in order to return the value.
return() {
    echo "$1"
}

# set_default function gives the ability to move the setting of default
# env variable from docker file to the script thereby giving the ability to the
# user override it durin container start.
set_default() {
    # docker initialized env variables with blank string and we can't just
    # use -z flag as usually.
    BLANK_STRING='""'

    VARIABLE="$1"
    DEFAULT="$2"

    if [[ -z "$VARIABLE" || "$VARIABLE" == "$BLANK_STRING" ]]; then

        if [ -z "$DEFAULT" ]; then
            error "You should specify default variable"
        else
            VARIABLE="$DEFAULT"
        fi
    fi

   return "$VARIABLE"
}

# Set default variables if needed.
BITCOIND_HOST=$(set_default "$BITCOIND_HOST" "127.0.0.1")
RPCUSER=$(set_default "$RPCUSER" "rpcuser")
RPCPASS=$(set_default "$RPCPASS" "rpcpass")
DEBUG=$(set_default "$DEBUG" "debug")
NETWORK=$(set_default "$NETWORK" "testnet")
CHAIN=$(set_default "$CHAIN" "bitcoin")
BACKEND="bitcoind"

EXT_IP=`curl -4s ident.me`

exec lnd \
    --noseedbackup \
    --logdir="/data" \
    "--$CHAIN.active" \
    "--$CHAIN.$NETWORK" \
    "--$CHAIN.node"="bitcoind" \
    "--$BACKEND.rpchost"="$BITCOIND_HOST" \
    "--$BACKEND.rpcuser"="$RPCUSER" \
    "--$BACKEND.rpcpass"="$RPCPASS" \
    "--$BACKEND.zmqpubrawblock=tcp://$BITCOIND_HOST:28332" \
    "--bitcoind.zmqpubrawtx=tcp://$BITCOIND_HOST:28333" \
    "--externalip=$EXT_IP" \
    --debuglevel="$DEBUG" \
    "$@"
