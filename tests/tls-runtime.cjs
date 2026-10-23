const assert = require('node:assert/strict');
const fs = require('node:fs');
const crypto = require('node:crypto');
const base = 'http://127.0.0.1/rtl';
const jar = {};
async function req(path, options = {}) {
  const response = await fetch(base + path, { ...options, headers: {
    cookie: Object.entries(jar).map(([k, v]) => k + '=' + v).join('; '), ...options.headers
  } });
  for (const line of response.headers.getSetCookie()) {
    const pair = line.split(';')[0], i = pair.indexOf('='); jar[pair.slice(0, i)] = pair.slice(i + 1);
  }
  return response;
}
(async () => {
  assert.equal((await req('/login')).status, 200);
  const login = await req('/api/authenticate', { method: 'POST', headers: {
    'content-type': 'application/json', 'x-xsrf-token': decodeURIComponent(jar['XSRF-TOKEN'])
  }, body: JSON.stringify({ authenticateWith: 'PASSWORD', authenticationValue: crypto.createHash('sha256').update('NodeTestRtlPassword20261023').digest('hex') }) });
  assert.equal(login.status, 200);
  const { token } = await login.json();
  const headers = { authorization: 'Bearer ' + token };
  const path = '/RTL/backup/node-1/channel-all.bak';
  if (process.argv[2] === 'fail') {
    const backup = fs.readFileSync(path);
    const response = await req('/api/lnd/getinfo', { headers });
    assert.ok(response.status >= 400);
    const body = await response.text();
    assert.ok(!body.includes('deadbeef') && !body.includes('PRIVATE KEY'));
    assert.equal((await req('/login')).status, 200);
    assert.deepEqual(fs.readFileSync(path), backup);
    console.log(JSON.stringify({ certificateErrorRejected: true, uiAvailable: true, backupPreserved: true }));
  } else {
    assert.equal((await req('/api/lnd/getinfo', { headers })).status, 200);
    assert.throws(() => fs.writeFileSync('/shared/cannot-write', 'test'), { code: 'EROFS' });
    assert.ok(!fs.readFileSync('/RTL/RTL-Config.json', 'utf8').includes(process.env.APP_PASSWORD));
    for (const file of ['/root/.lnd/tls.key', '/root/.lnd/data/chain/bitcoin/regtest/wallet.db', '/shared/tls.key', '/shared/wallet.db']) assert.equal(fs.existsSync(file), false);
    console.log(JSON.stringify({ verifiedConnection: true, sharedVolumeReadOnly: true, privateStateAbsent: true }));
  }
})().catch(error => { console.error(error); process.exit(1); });
