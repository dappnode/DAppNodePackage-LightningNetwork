# Lightning Network DAppNode Package

[![DAppNodeStore Available](https://img.shields.io/badge/DAppNodeStore-Available-brightgreen.svg)](http://my.admin.dnp.dappnode.eth/#/installer/ln.dnp.dappnode.eth)

This package makes it easy to deploy a [Lightning Network Daemon](https://github.com/lightningnetwork/lnd) in a DAppNode. It also includes a web interface [lncli-web](https://github.com/mably/lncli-web) to manage the node.

[lightning-network-summary](https://lightning.network/lightning-network-summary.pdf)
[The Bitcoin Lightning Network: Paper (PDF)](https://lightning.network/lightning-network-paper.pdf)

# Prerequisites

- git

   Install [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) commandline tool.

- docker

   Install [docker](https://docs.docker.com/engine/installation). The community edition (docker-ce) will work. In Linux make sure you grant permissions to the current user to use docker by adding current user to docker group, `sudo usermod -aG docker $USER`. Once you update the users group, exit from the current terminal and open a new one to make effect.

- docker-compose

   Install [docker-compose](https://docs.docker.com/compose/install)
   
**Note**: Make sure you can run `git`, `docker ps`, `docker-compose` without any issue and without sudo command.


## Building

`docker-compose build`

## Running

### Start

`docker-compose up -d`

### View logs

`docker-compose logs -f`

### Stop

`docker-compose down`

## Environment variables

You can edit the `docker-compose.yml` and add extra options, such a:

| name | default |
| ---- | ------- |
| RPCUSER | dappnode |
| RPCPASS | dappnode |
| BITCOIND_HOST | my.bitcoin.dnp.dappnode.eth |
| NETWORK | mainnet |
| SET_SERVERHOST | 0.0.0.0 |
| ALIAS |  |
| EXT_IP |  |

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details

## Note

This is early stage software
