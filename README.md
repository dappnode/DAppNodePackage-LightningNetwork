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
| ALIAS |  |
| COLOR |  |
| EXT_IP |  |

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details


# Using the LN package

**Before downloading the Ligtning Package, we assume previous understanding of the Lightning Network. Otherwise, please have a look at the following documents: 

[lightning-network-summary](https://lightning.network/lightning-network-summary.pdf), [The Bitcoin Lightning Network: Paper (PDF)](https://lightning.network/lightning-network-paper.pdf) and other valuable resources about LN [here](https://lnroute.com/)** 

* This package contains both [Lightning Network Daemon](https://github.com/lightningnetwork/lnd) and [Ride The Lightning](https://github.com/ShahanaFarooqui/RTL) web interface

* You need to have the Bitcoin node package (without pruning) installed and fully synced for the package to work properly. You don't need to wait for the Bitcoin Core node to be fully synced to install the LN package, but it won't be functional until the node is synced.

* The private keys of your LN wallet are stored in your LN node data volume. **Please follow the guide about backups below in this document to prevent loss of funds. We don't offer a seed backup mechanism so this is the only way to recover your funds in case something goes wrong**.

* When installing LN in DAppNode there will be two sets of username/password: 
    * One to connect to the Bitcoin node, RPCUSER and RPCPASS (make sure they are the same as the Bitcoin package) and 
    * Another one, RTL_PASSWORD, to allow  access to the web UI and execute transactions/use the node. 
    * Remember to change these if you are sharing your DAppNode with others! Take in account that **if you give admin access to your DAppNode to anyone, that access implies full control of your LN node** including accessing your funds.

* You can connect your favourite LN mobile wallet  by opening a private channel with your node.
 
* When updating this package, volumes will not be affected. You can access an updated version of your LN node witbout risk of losing any funds. Do not remove the volume though, or you will lose the funds on your node if you have not followed ths instructions for backup.

## Accessing the ADMIN UI

Once the node is synced, you can access your LN node [admin UI here](https://lightning-network.dappnode)

## How to download macaroons

Usually Lightning Network applications require files called *macaroons* for authorizations to perform operations on the LND node. There are many types depending on the level of access.

To download the admin macaroon, you should go to the Admin panel of DAppnode: 

Packages -> lightning-network -> File manager

Then input in the "Download from DNP" field:

```
/config/data/chain/bitcoin/mainnet/admin.macaroon
```

## How to use Joule extension with DAppNode

Joule is an extension available for many browsers which lets you use your node to make payments, invoices, open channels and more. Check the website: https://lightningjoule.com/

* To run Joule, first you need to download these macaroons in a safe folder, as described above:

```
/config/data/chain/bitcoin/mainnet/admin.macaroon
/config/data/chain/bitcoin/mainnet/readonly.macaroon
```

* When asked on the type of node, select Remote and then enter the following url: 

   https://lightning-network.dappnode:8080
   * You will need to accept the SSL certificate in the next step

* Upload the macaroons, choose a password to encrypt the data, and you're ready to go!


* **Enjoy!** But be aware both LND and RTL are beta software .Only use funds you can afford to lose.  Don't be completely #Reckless ;)





