# Lightning Network Dappnode package

Run LND and the Ride The Lightning web interface as two services. This update adopts the separate-service and official-image approach proposed in [PR #24](https://github.com/dappnode/DAppNodePackage-LightningNetwork/pull/24), with current security versions and verified RTL-to-LND TLS.

| Service | Upstream | Package changes |
| --- | --- | --- |
| `lnd` | Official `lightninglabs/lnd:v0.21.4-beta`, pinned by digest | Startup configuration, migration guard and refreshed system CA trust. |
| `rtl` | Official `shahanafarooqui/rtl:v0.15.15`, pinned by digest; Node 22.23.4 | Retain the official frontend/dependencies, apply our verified-TLS backend patch and refresh system CA trust. |

The provisional package version is **0.5.0** because the service layout and operator configuration change. Only amd64 is currently validated.

## Installation and UI

Install a compatible, synchronized Bitcoin package. Choose an RTL password in the Dappnode installation form, then open `http://rtl.lightning-network.dappnode` and sign in with that password. The password is provided only to RTL. LND generates the wallet's credentials and TLS certificates itself; wallet creation/unlock works through RTL.

**Existing installations must follow [MIGRATION.md](MIGRATION.md)** before updating. A direct LND 0.14.1 → 0.21.4 database upgrade failed in our isolated test. The tested intermediate release is LND 0.15.5.

## Service and data boundaries

- `lndconfig_data` stays mounted at `/root/.lnd` in LND. The wallet database and TLS private key are never mounted into RTL.
- `lnd_shared` contains the public TLS certificate(s) and admin macaroon. LND writes it; RTL mounts it read-only at `/shared`.
- `lndconfig_backup` remains the dedicated RTL backup volume, now mounted at `/RTL/backup`.
- Only LND's peer port `9735` is published on the host. RTL and LND REST use Dappnode's internal service network; gRPC retains LND's default local listener.

RTL remains an administrator of LND through its admin macaroon; separating private-key storage does not restrict the wallet operations that this credential authorizes. Package backups contain sensitive wallet/credential material and must be protected.

## Verified TLS

RTL uses `https://lnd.lightning-network.dappnode:8080`. LND includes that hostname in its certificate. The RTL patch trusts `/shared/tls.cert` and, while encrypted-key LND is locked, `/shared/tls.cert.tmp`. It retains hostname and expiry verification, binds requests to the configured HTTPS origin, and follows no credentialed redirects.

Each new connection reads the current local public certificate files. Missing, malformed, untrusted, expired or wrong-hostname certificates fail safely while the UI remains available. Certificate renewal and temporary-to-permanent unlock transitions need no RTL restart. No private-key loading, network trust discovery, insecure retry or automatic payment replay is used.

The TLS settings and credentialed origin are server-owned. The browser settings API cannot replace them. LND's raw configuration file, which can contain Bitcoin RPC credentials, is not mounted into RTL. The separate upstream CLN WebSocket transport is outside this LND package's scope.

## Configuration

| Service | Variables |
| --- | --- |
| `rtl` | `APP_PASSWORD` — required, non-default UI password. |
| `lnd` | `NETWORK` (`mainnet` by default), `RPCUSER`, `RPCPASS`, `BITCOIND_HOST`, optional `BITCOIND_RPCPORT`, `BITCOIND_RPC_POLLING`, `ALIAS`, `COLOR`, `EXT_IP`. |
| `lnd` | `LND_MIGRATION_CONFIRMED` — only set after the documented staged migration of an existing unmarked wallet. |

TLS certificate/macaroons paths and service hostname are set by LND's wrapper arguments. RTL's matching trust/origin configuration is installed by its wrapper. Existing LND configuration files are retained; the wrapper does not rewrite the operator's Bitcoin credentials into a shared file.

## Build and validation

```sh
docker compose build
```

For local validation, the harness defaults use these image aliases:

```sh
docker build -t codex/lightning-lnd:split-20261023 buildLnd
docker build -t codex/lightning-rtl:split-20261023 buildRtl
python3 tests/runtime-smoke.py --output /tmp/lightning-runtime-private
python3 tests/regtest-smoke.py --fresh --output /tmp/lightning-fresh-private
python3 tests/regtest-smoke.py --fresh --encrypted-tls --output /tmp/lightning-encrypted-private
```

Build the pinned Bitcoin/legacy LND test fixtures and run the staged regression using the commands in `.github/workflows/node-runtime-test.yml`. All tests use synthetic credentials, unfunded wallets, disposable volumes and an internal Docker network. Do not distribute raw wallet logs; share the JSON summaries only.

The RTL image build checks the pinned source commit, applies `buildRtl/patches/rtl-lnd-tls-verification.patch`, compiles the patched backend and runs all 397 backend tests as an unprivileged user. The official frontend is retained. The runtime harness covers UI/password/CSRF, WebSocket upgrade, wrong/untrusted certificates, read-only sharing, renewal, backup preservation and independent service restarts.

No funded channels, payment/watchtower database migration, ARM64 build or Angular browser suite is certified by these tests. This source update is not an automatic production-wallet migration.
