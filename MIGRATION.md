# Lightning application security update

This patch upgrades RTL from 0.12.1 to 0.15.15 and LND from 0.14.1-beta to 0.21.4-beta. It retains patched Node 22.23.4, refreshes system trust, pins the RTL source commit and verifies the LND release archive checksum. Set a non-default `APP_PASSWORD` before starting RTL. The JSON template now uses current lowercase authentication/settings keys and follows `NETWORK` for its macaroon path.

## Existing wallets

**The direct LND 0.14.1 → 0.21.4 jump fails in the isolated regression test** with `top-level bucket "chan-id-bucket" already exists`. Do not install the new image over an old wallet and assume startup will migrate it. The wrapper refuses an existing unmarked wallet unless `LND_MIGRATION_CONFIRMED=true` is set. Fresh installations receive a marker and do not need that setting.

The tested route is **0.14.1-beta → 0.15.5-beta → 0.21.4-beta**. It preserves an unfunded synthetic regtest wallet's identity, opens its databases, creates a new address and invoice, and retains identity after restart/unlock. The intermediate release is a temporary offline migration tool, not the target production runtime. It was tested against Bitcoin Core 25.2 because the old LND binary cannot parse Bitcoin Core 31.1's changed RPC warnings format. Fresh 0.21.4 operation is separately tested against Bitcoin Core 31.1.

For a real installation, stop LND cleanly, take a complete offline backup of the `.lnd` directory and channel backups, and rehearse this path on a protected copy. Run only one instance of the wallet identity; never connect an old copy in parallel or roll an actively used migrated channel database back to its pre-upgrade snapshot. Follow the upstream operator migration guidance. Start the intermediate release on the real database only as part of that controlled upgrade, unlock and verify it, stop it cleanly, then install the new package and set `LND_MIGRATION_CONFIRMED=true`. Check node identity, channels, balances and backup state. Keep the intermediate image off the normal public service path.

This patch's regression uses no channels, payments or funded wallets. It does not certify migration of every historical channel/payment/watchtower database or external plugin, or replace an operator's backup/recovery review. Only amd64 is currently validated with the official upstream images. The old package's seedless-wallet flag and dangling macaroon link are removed; LND handles certificate and macaroon generation.

`BITCOIND_RPCPORT` can select the appropriate RPC port. `BITCOIND_RPC_POLLING=true` selects RPC polling; otherwise the existing ZMQ ports remain in use. The package no longer queries an external IP service during startup; set `EXT_IP` when advertisement is needed.

## Reproduce the regression

The GitHub Actions workflow builds the checksum-pinned Bitcoin and legacy LND fixtures and runs both the staged old-wallet test and fresh-wallet test. All containers use an internal Docker network, disposable volumes and zero wallet balance. Raw wallet logs contain generated test material and must not be distributed as part of the PR handoff.

Sources:

- [RTL security release](https://github.com/Ride-The-Lightning/RTL/releases/tag/v0.15.15)
- [LND target release](https://github.com/lightningnetwork/lnd/releases/tag/v0.21.4-beta)
- [LND operator upgrade guidance](https://docs.lightning.engineering/lightning-network-tools/lnd/run-lnd)
- [LND migration guidance](https://docs.lightning.engineering/lightning-network-tools/lnd/migrating-lnd)


## Split-service update (package 0.5.0)

This revision adopts PR #24's two-service layout using current, digest-pinned official images. LND stays at 0.21.4-beta; RTL stays at 0.15.15 with Node 22.23.4 and the verified-TLS source patch. The change from one service to `lnd` and `rtl` requires an operator configuration review even if the wallet is already on LND 0.21.4.

1. Stop the old package cleanly and take a complete offline backup of its `.lnd` data and RTL channel backups. Complete/rehearse the staged LND migration above when starting from 0.14.1. Keep only one running instance of the wallet identity.
2. Preserve the named `lndconfig_data` and `lndconfig_backup` volumes. The new `lnd` service must mount the existing `.lnd` contents at `/root/.lnd`; the new `rtl` service must mount the existing backup contents at `/RTL/backup`. The logical volume names are deliberately retained. Review any custom bind mounts or disk locations before installing; service names and mount destinations have changed.
3. Reapply Bitcoin RPC credentials, network, alias and other LND settings to **`lnd`**. Supply the desired UI password as **`rtl.APP_PASSWORD`** through the installation form or Config. Environment values that belonged to the old single service must not be assumed to move automatically to the new services.
4. Start with the new `lnd_shared` volume mounted read/write in LND and read-only in RTL. LND generates its public certificate at `/shared/tls.cert` (temporarily `/shared/tls.cert.tmp` in encrypted-key mode) and admin macaroon at `/shared/admin.macaroon`. Its private TLS key stays at `/root/.lnd/tls.key`. Changing the certificate path can cause LND to generate a new TLS certificate/key pair; it does not change the Lightning wallet identity. External clients that pinned the old public certificate must update their trust through a controlled local export.
5. Set `lnd.LND_MIGRATION_CONFIRMED=true` only after the required legacy migration, when an existing wallet has no readiness marker. Unlock through RTL. Verify wallet identity, channels, balances and backup state before returning the node to normal use. The UI is now `http://rtl.lightning-network.dappnode`; LND REST is `https://lnd.lightning-network.dappnode:8080`.

RTL has no mount of the wallet database, TLS private key or raw LND configuration. Its read-only shared admin macaroon still authorizes wallet administration. Export a public certificate from the LND service's `/shared/tls.cert` when configuring a separate trusted client; never share `tls.key`. Local `lncli` use now needs `--tlscertpath=/shared/tls.cert --macaroonpath=/shared/admin.macaroon` in addition to the appropriate `--network`.

The isolated regression verifies fresh wallet creation through RTL (including encrypted-key TLS), migration of an unfunded 0.14.1 wallet through 0.15.5 into the new LND service, preserved wallet identity and zero balance, and independent RTL/LND restarts. It reuses the test wallet volume directly. Installation on an actual Dappnode with customized mounts, funded channels or historical plugin databases remains an operator acceptance step; no live installation is performed by this change.
