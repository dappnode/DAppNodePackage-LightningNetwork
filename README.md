# Lightning Network DAppNode Package

[![DAppNodeStore Available](https://img.shields.io/badge/DAppNodeStore-Available-brightgreen.svg)](http://my.admin.dnp.dappnode.eth/#/installer/ln.dnp.dappnode.eth)

This package makes it easy to deploy a [Lightning Network Daemon](https://github.com/lightningnetwork/lnd) in a DAppNode. It also includes a web interface [Ride The Lightning](https://github.com/ShahanaFarooqui/RTL/) to manage the node.

[Summary](https://lightning.network/lightning-network-summary.pdf)

[The Bitcoin Lightning Network: Paper (PDF)](https://lightning.network/lightning-network-paper.pdf)

# Warning :warning:

Both LND and RTL are beta software. Don't be completely #reckless.

It is recommended to save backups every time you update the package, or even from time to time with a cron job.
For many reasons we don't save any seed to restore the wallet, and having an up to date backup is crucial to not lose any funds in case something bad happens.

# Backup LND data

LND data is stored permanently in a docker volume, but it is recommended to save it apart in case of an update or migration.
Follow this steps:

```
docker run --rm --volumes-from DAppNodePackage-lightning-network.dnp.dappnode.eth -v $(pwd):/backup alpine tar cvzf /backup/backup_lnd.tar.gz /root/.lnd
```
A file named `backup_lnd.tar.gz` will be created in your current path.

To restore it, proceed as follows:
```
docker run --rm --volumes-from DAppNodePackage-lightning-network.dnp.dappnode.eth -v $(pwd):/backup alpine sh -c "cd /root/.lnd && tar xvzf /backup/backup_lnd.tar.gz --strip 2"
    
```
then restart the package from the admin interface.


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

