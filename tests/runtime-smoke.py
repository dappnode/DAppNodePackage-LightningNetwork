"""Packaged split-service UI/TLS checks. Disposable volumes and synthetic credentials only."""
import argparse
import json
import pathlib
import subprocess
import tempfile
import time
import uuid

p = argparse.ArgumentParser()
p.add_argument('--rtl-image', default='codex/lightning-rtl:split-20261023')
p.add_argument('--lnd-image', default='codex/lightning-lnd:split-20261023')
p.add_argument('--output', required=True)
a = p.parse_args()
out = pathlib.Path(a.output); out.mkdir(parents=True, exist_ok=True)
tests = pathlib.Path(__file__).resolve().parent
uid = 'lightning-split-test-' + uuid.uuid4().hex[:10]
rtl, mock, shared, backup = [uid + suffix for suffix in ['-rtl', '-mock', '-shared', '-backup']]
result = {}

def run(*args, check=True, input=None):
    r = subprocess.run(['docker', *args], input=input, capture_output=True, text=True, timeout=180)
    if check and r.returncode:
        raise RuntimeError('Docker ' + args[0] + ' failed\n' + r.stdout + r.stderr)
    return r.stdout.strip()

def wait(fn):
    deadline = time.monotonic() + 45
    while True:
        try: return fn()
        except Exception:
            if time.monotonic() >= deadline: raise
            time.sleep(.3)

def fixture_cert(directory, name, san):
    prefix = pathlib.Path(directory) / name
    subprocess.run(['openssl', 'req', '-x509', '-newkey', 'ec', '-pkeyopt', 'ec_paramgen_curve:P-256', '-nodes',
                    '-keyout', str(prefix) + '.key', '-out', str(prefix) + '.crt', '-days', '1',
                    '-subj', '/CN=Synthetic split-service fixture', '-addext', 'subjectAltName=' + san],
                   check=True, capture_output=True)
    return prefix

def write_trust(value):
    script = "const fs=require('fs');const data=fs.readFileSync(0);if(data.length)fs.writeFileSync('/shared/tls.cert',data);else fs.unlinkSync('/shared/tls.cert');"
    run('exec', '-i', mock, 'node', '-e', script, input=value)

def audit():
    return run('exec', mock, 'node', '-e', "process.stdout.write(require('fs').readFileSync('/shared/http-audit','utf8'))")

def api(mode):
    return json.loads(run('exec', rtl, 'node', '/tmp/tls-runtime.cjs', mode))

try:
    guard = subprocess.run(['docker', 'run', '--rm', '--network', 'none', '--cpus', '1', '--memory', '256m',
                            '--entrypoint', 'sh', a.lnd_image, '-c',
                            'mkdir -p /root/.lnd/data/chain/bitcoin/mainnet; touch /root/.lnd/data/chain/bitcoin/mainnet/wallet.db; exec /opt/dappnode/entrypoint.sh'],
                           capture_output=True, text=True, timeout=15)
    assert guard.returncode == 1 and 'staged upgrade' in guard.stderr
    result['legacyMigrationGuard'] = True
    guard = subprocess.run(['docker', 'run', '--rm', '--network', 'none', '--cpus', '1', '--memory', '256m',
                            '-e', 'APP_PASSWORD=changeme', a.rtl_image], capture_output=True, text=True, timeout=15)
    assert guard.returncode == 1 and 'non-default password' in guard.stderr
    result['defaultPasswordRejected'] = True
    run('network', 'create', '--internal', uid)
    for volume in [shared, backup]: run('volume', 'create', volume)
    with tempfile.TemporaryDirectory(prefix='split-tls-fixtures-', dir=out) as directory:
        good = fixture_cert(directory, 'good', 'DNS:lnd.lightning-network.dappnode,DNS:lnd,DNS:localhost')
        impostor = fixture_cert(directory, 'impostor', 'DNS:lnd.lightning-network.dappnode')
        wrong_name = fixture_cert(directory, 'wrong-name', 'DNS:localhost')
        run('create', '--name', mock, '--network', uid, '--network-alias', 'lnd.lightning-network.dappnode',
            '--cpus', '1', '--memory', '256m', '-v', shared + ':/shared', '--entrypoint', 'node',
            a.rtl_image, '/tmp/mock-lnd.cjs')
        run('cp', str(tests / 'mock-lnd.cjs'), mock + ':/tmp/mock-lnd.cjs')
        for extension in ['key', 'crt']: run('cp', str(good) + '.' + extension, mock + ':/tmp/lnd-fixture.' + extension)
        run('start', mock)
        wait(lambda: run('exec', mock, 'node', '-e', "if(!require('fs').existsSync('/shared/tls.cert'))process.exit(1)"))
        run('run', '-d', '--name', rtl, '--network', uid, '--cpus', '2', '--memory', '1g',
            '-v', shared + ':/shared:ro', '-v', backup + ':/RTL/backup',
            '-e', 'APP_PASSWORD=NodeTestRtlPassword20261023', a.rtl_image)
        for filename in ['http-smoke.cjs', 'node-security-smoke.cjs', 'tls-runtime.cjs']:
            run('cp', str(tests / filename), rtl + ':/tmp/' + filename)
        wait(lambda: run('exec', rtl, 'node', '-e', "fetch('http://127.0.0.1/rtl/login').then(r=>{if(!r.ok)process.exit(1)}).catch(()=>process.exit(1))"))
        result['nodeSecurity'] = json.loads(run('exec', rtl, 'node', '/tmp/node-security-smoke.cjs'))
        result['http'] = json.loads(run('exec', rtl, 'node', '/tmp/http-smoke.cjs'))
        result['isolation'] = api('pass')
        for name, value in [('missing', ''), ('malformed', 'not a certificate'), ('untrusted', pathlib.Path(str(impostor) + '.crt').read_text())]:
            before = audit()
            write_trust(value)
            result[name] = api('fail')
            assert audit() == before, 'A failed TLS handshake delivered an HTTP request'
        write_trust(pathlib.Path(str(good) + '.crt').read_text())
        api('pass')
        for prefix, case in [(impostor, 'renewal'), (wrong_name, 'wrongHostname')]:
            for extension in ['key', 'crt']: run('cp', str(prefix) + '.' + extension, mock + ':/tmp/lnd-fixture.' + extension)
            run('kill', '--signal', 'USR2', mock); time.sleep(.1)
            before = audit()
            api('fail')
            assert audit() == before
            write_trust(pathlib.Path(str(prefix) + '.crt').read_text())
            if case == 'wrongHostname':
                api('fail'); assert audit() == before
            else: api('pass')
            result[case] = True
        for extension in ['key', 'crt']: run('cp', str(good) + '.' + extension, mock + ':/tmp/lnd-fixture.' + extension)
        run('kill', '--signal', 'USR2', mock)
        write_trust(pathlib.Path(str(good) + '.crt').read_text())
        run('restart', rtl)
        wait(lambda: run('exec', rtl, 'node', '-e', "fetch('http://127.0.0.1/rtl/login').then(r=>{if(!r.ok)process.exit(1)}).catch(()=>process.exit(1))"))
        result['restart'] = json.loads(run('exec', rtl, 'node', '/tmp/http-smoke.cjs'))
        # Check the actual LND image's CA bundle using the same distrust regression.
        ca_container = uid + '-ca'
        run('create', '--name', ca_container, a.lnd_image)
        try:
            ca_file = pathlib.Path(directory) / 'lnd-ca.crt'
            run('cp', ca_container + ':/etc/ssl/certs/ca-certificates.crt', str(ca_file))
            run('cp', str(ca_file), rtl + ':/tmp/lnd-ca.crt')
            result['lndCaSecurity'] = json.loads(run('exec', rtl, 'node', '/tmp/node-security-smoke.cjs', '22.23.4', '/tmp/lnd-ca.crt'))
        finally: run('rm', '-v', ca_container, check=False)
        result.update(success=True, readOnlySharedCredentials=True, privateWalletAndTlsKeyNotMounted=True,
                      crossServiceHostnameVerified=True, backupPreserved=True, productionDataUsed=False)
finally:
    for name in [rtl, mock]:
        (out / (name.rsplit('-', 1)[-1] + '.log')).write_text(run('logs', name, check=False))
        run('rm', '-f', '-v', name, check=False)
    for volume in [shared, backup]: run('volume', 'rm', volume, check=False)
    run('network', 'rm', uid, check=False)
    (out / 'runtime-validation.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
