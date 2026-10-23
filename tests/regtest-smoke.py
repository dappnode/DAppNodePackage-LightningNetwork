"""Split-service wallet lifecycle on an internal network; no funded or production state."""
import argparse
import base64
import json
import pathlib
import subprocess
import time
import uuid

p = argparse.ArgumentParser()
p.add_argument('--lnd-image', default='codex/lightning-lnd:split-20261023')
p.add_argument('--rtl-image', default='codex/lightning-rtl:split-20261023')
p.add_argument('--bitcoin-image', default='codex/bitcoin-regtest:31.1')
p.add_argument('--old-image', default='codex/lnd-legacy-regtest:0.14.1')
p.add_argument('--bridge-image')
p.add_argument('--fresh', action='store_true')
p.add_argument('--encrypted-tls', action='store_true')
p.add_argument('--output', required=True)
a = p.parse_args()
out = pathlib.Path(a.output); out.mkdir(parents=True, exist_ok=True)
tests = pathlib.Path(__file__).resolve().parent
uid = 'lightning-split-regtest-' + uuid.uuid4().hex[:10]
btc, old, lnd, rtl, data, shared, backup = [uid + x for x in ['-btc', '-old', '-lnd', '-rtl', '-data', '-shared', '-backup']]
password = base64.b64encode(b'Only-An-Unfunded-Regtest-Wallet-2026').decode()
result = {}

# This test client trusts only public files in read-only mounts, never an unverified peer.
REST_CLIENT = """
const fs=require('fs'),https=require('https');
const input=JSON.parse(fs.readFileSync(0,'utf8'));
const ca=input.paths.filter(p=>fs.existsSync(p)).map(p=>fs.readFileSync(p));
if(!ca.length)process.exit(1);
const req=https.request(input.url,{ca,rejectUnauthorized:true,method:input.body?'POST':'GET',headers:{'content-type':'application/json'}},res=>{
 let body='';res.on('data',c=>body+=c);res.on('end',()=>{if(res.statusCode>=400)process.exit(1);process.stdout.write(body)});
});req.on('error',()=>process.exit(1));req.setTimeout(5000,()=>req.destroy());if(input.body)req.write(JSON.stringify(input.body));req.end();
"""

def run(*args, check=True, input=None):
    r = subprocess.run(['docker', *args], capture_output=True, text=True, input=input, timeout=180)
    if check and r.returncode:
        # stdout from the seed endpoint must never be included in a diagnostic.
        raise RuntimeError('Docker ' + args[0] + ' failed\n' + r.stderr[-2000:])
    return r.stdout.strip()

def wait(fn, timeout=70):
    deadline = time.monotonic() + timeout
    while True:
        try: return fn()
        except Exception:
            if time.monotonic() >= deadline: raise
            time.sleep(.4)

def btc_rpc(*args):
    value = run('exec', btc, 'bitcoin-cli', '-regtest', '-rpcuser=test', '-rpcpassword=fixture', *args)
    try: return json.loads(value)
    except json.JSONDecodeError: return value

def rest(name, path, body=None):
    prefix = '/shared' if name == lnd else '/lnd'
    host = 'lnd.lightning-network.dappnode' if name == lnd else name
    value = run('run', '--rm', '-i', '--network', uid, '-v', data + ':/lnd:ro', '-v', shared + ':/shared:ro',
                '--entrypoint', 'node', a.rtl_image, '-e', REST_CLIENT,
                input=json.dumps({'url': 'https://' + host + ':8080' + path, 'paths': [prefix + '/tls.cert', prefix + '/tls.cert.tmp'], 'body': body}))
    return json.loads(value)

def cli(name, *args):
    options = ['--tlscertpath=/shared/tls.cert', '--macaroonpath=/shared/admin.macaroon'] if name == lnd else []
    return json.loads(run('exec', name, 'lncli', '--network=regtest', *options, *args))

def rtl_ready():
    return run('exec', rtl, 'node', '-e', "fetch('http://127.0.0.1/rtl/login').then(r=>{if(!r.ok)process.exit(1)}).catch(()=>process.exit(1))")

def wallet_operation(operation):
    wait(rtl_ready); wait(lambda: rest(lnd, '/v1/state'))
    temporary = run('exec', lnd, 'sh', '-c', 'test -s /shared/tls.cert.tmp && echo present || echo absent') == 'present'
    if a.encrypted_tls: assert temporary
    response = json.loads(run('exec', '-i', rtl, 'node', '/tmp/rtl-wallet-unlock.cjs', operation, input=password))
    if a.encrypted_tls:
        wait(lambda: run('exec', lnd, 'sh', '-c', 'test -s /shared/tls.cert && test ! -e /shared/tls.cert.tmp'))
    response['temporaryCertificateBeforeOperation'] = temporary
    response['permanentCertificateAfterOperation'] = True
    return response

def http_smoke():
    return json.loads(run('exec', '-e', 'EXPECTED_LND_ALIAS=UnfundedRegtest', rtl, 'node', '/tmp/http-smoke.cjs'))

def start_legacy(image):
    run('run', '-d', '--name', old, '--network', uid, '--cpus', '2', '--memory', '1g',
        '-v', data + ':/root/.lnd', '--entrypoint', 'lnd', image,
        '--bitcoin.active', '--bitcoin.regtest', '--bitcoin.node=bitcoind',
        '--bitcoind.rpchost=bitcoin-fixture:18443', '--bitcoind.rpcuser=test', '--bitcoind.rpcpass=fixture',
        '--bitcoind.zmqpubrawblock=tcp://bitcoin-fixture:28332', '--bitcoind.zmqpubrawtx=tcp://bitcoin-fixture:28333',
        '--restlisten=0.0.0.0:8080', '--tlsextradomain=' + old, '--alias=UnfundedRegtest')

try:
    assert a.fresh or a.bridge_image, 'Legacy state requires the documented intermediate version.'
    assert not a.encrypted_tls or a.fresh
    run('network', 'create', '--internal', uid)
    for volume in [data, shared, backup]: run('volume', 'create', volume)
    if a.encrypted_tls:
        run('run', '--rm', '--network', 'none', '-v', data + ':/root/.lnd', '--entrypoint', 'sh', a.lnd_image,
            '-c', 'printf "[Application Options]\\ntlsencryptkey=true\\n" > /root/.lnd/lnd.conf')
    run('run', '-d', '--name', btc, '--network', uid, '--network-alias', 'bitcoin-fixture',
        '--cpus', '2', '--memory', '1g', a.bitcoin_image, '-regtest', '-server', '-listen=0',
        '-rpcbind=0.0.0.0', '-rpcallowip=0.0.0.0/0', '-rpcuser=test', '-rpcpassword=fixture', '-fallbackfee=0.0002',
        '-zmqpubrawblock=tcp://0.0.0.0:28332', '-zmqpubrawtx=tcp://0.0.0.0:28333')
    wait(lambda: btc_rpc('getblockchaininfo'))
    bitcoin_version = btc_rpc('getnetworkinfo')['version']
    btc_rpc('-named', 'createwallet', 'wallet_name=fixture')
    btc_rpc('generatetoaddress', '101', btc_rpc('getnewaddress'))
    before = None; bridge_info = None
    if not a.fresh:
        start_legacy(a.old_image)
        seed = wait(lambda: rest(old, '/v1/genseed'))['cipher_seed_mnemonic']
        rest(old, '/v1/initwallet', {'wallet_password': password, 'cipher_seed_mnemonic': seed}); del seed
        before = wait(lambda: cli(old, 'getinfo'))
        assert before['version'].startswith('0.14.1')
        run('stop', '--time', '30', old); run('rm', old)
        start_legacy(a.bridge_image)
        wait(lambda: rest(old, '/v1/unlockwallet', {'wallet_password': password}))
        bridge_info = wait(lambda: cli(old, 'getinfo'))
        assert bridge_info['identity_pubkey'] == before['identity_pubkey']
        run('stop', '--time', '30', old); run('rm', old)
    run('run', '-d', '--name', lnd, '--network', uid, '--network-alias', 'lnd.lightning-network.dappnode',
        '--cpus', '2', '--memory', '1g', '-v', data + ':/root/.lnd', '-v', shared + ':/shared',
        '-e', 'NETWORK=regtest', '-e', 'BITCOIND_HOST=bitcoin-fixture', '-e', 'BITCOIND_RPCPORT=18443',
        '-e', 'BITCOIND_RPC_POLLING=true', '-e', 'RPCUSER=test', '-e', 'RPCPASS=fixture',
        '-e', 'LND_MIGRATION_CONFIRMED=true', '-e', 'ALIAS=UnfundedRegtest', a.lnd_image)
    run('run', '-d', '--name', rtl, '--network', uid, '--cpus', '2', '--memory', '1g',
        '-v', shared + ':/shared:ro', '-v', backup + ':/RTL/backup',
        '-e', 'APP_PASSWORD=NodeTestRtlPassword20261023', a.rtl_image)
    for filename in ['rtl-wallet-unlock.cjs', 'http-smoke.cjs']:
        run('cp', str(tests / filename), rtl + ':/tmp/' + filename)
    operation = wallet_operation('init' if a.fresh else 'unlock')
    after = wait(lambda: cli(lnd, 'getinfo'))
    if before is None: before = after
    assert after['identity_pubkey'] == before['identity_pubkey']
    assert after['version'].startswith('0.21.4') and after['chains'][0]['network'] == 'regtest'
    assert cli(lnd, 'newaddress', 'p2wkh')['address'].startswith('bcrt')
    assert cli(lnd, 'addinvoice', '--amt', '1', '--memo', 'isolated-split-test')['payment_request'].startswith('lnbcrt')
    http = http_smoke()
    isolation = json.loads(run('exec', rtl, 'node', '-e', "const fs=require('fs'),assert=require('assert');assert(!fs.existsSync('/root/.lnd/tls.key'));assert(!fs.existsSync('/shared/tls.key'));assert.throws(()=>fs.writeFileSync('/shared/test','x'));console.log(JSON.stringify({sharedReadOnly:true,walletAndPrivateKeyAbsent:true}))"))
    lnd_env = json.loads(run('inspect', lnd))[0]['Config']['Env']
    assert not any(value.startswith('APP_PASSWORD=') for value in lnd_env)
    run('restart', rtl); wait(rtl_ready)
    rtl_restart = http_smoke()
    # Restart LND alone: RTL must reread temporary/current public certificates without its own restart.
    run('restart', '--time', '30', lnd)
    unlock_restart = wallet_operation('unlock')
    restarted = wait(lambda: cli(lnd, 'getinfo'))
    assert restarted['identity_pubkey'] == before['identity_pubkey']
    assert int(cli(lnd, 'walletbalance')['total_balance']) == 0
    after_lnd_restart = http_smoke()
    result = {'success': True, 'lndVersion': after['version'], 'bitcoinVersion': bitcoin_version,
              'freshInstallTest': a.fresh, 'encryptedTlsKey': a.encrypted_tls, 'rtlWalletOperation': operation,
              'intermediateRelease': bridge_info['version'] if bridge_info else None,
              'legacyDatabaseMigrated': not a.fresh, 'nodeIdentityPreserved': True,
              'rtlRealLnd': http, 'rtlRestart': rtl_restart, 'lndRestartRtlUnlock': unlock_restart,
              'rtlAfterLndRestart': after_lnd_restart, 'isolation': isolation,
              'uiPasswordAbsentFromLnd': True, 'walletBalanceSatoshis': 0,
              'externalPeers': False, 'paymentsSent': False, 'productionDataUsed': False}
finally:
    for name in [old, lnd, rtl, btc]:
        (out / (name.rsplit('-', 1)[-1] + '-private.log')).write_text(run('logs', name, check=False))
        run('rm', '-f', '-v', name, check=False)
    for volume in [data, shared, backup]: run('volume', 'rm', volume, check=False)
    run('network', 'rm', uid, check=False)
    (out / 'regtest-validation.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
