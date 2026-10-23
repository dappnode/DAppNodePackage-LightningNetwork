// Disposable regtest wallet only. Read the synthetic password from stdin; never print it.
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const fs = require('node:fs');
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
  const password = fs.readFileSync(0, 'utf8').trim();
  assert.equal((await req('/login')).status, 200);
  const login = await req('/api/authenticate', { method: 'POST', headers: {
    'content-type': 'application/json', 'x-xsrf-token': decodeURIComponent(jar['XSRF-TOKEN'])
  }, body: JSON.stringify({ authenticateWith: 'PASSWORD', authenticationValue: crypto.createHash('sha256').update('NodeTestRtlPassword20261023').digest('hex') }) });
  assert.equal(login.status, 200);
  const { token } = await login.json();
  // Match the UI's node-option initialization before making a wallet request.
  const setup = await req('/api/lnd/wallet/updateSelNodeOptions', { headers: { authorization: 'Bearer ' + token } });
  assert.ok([200, 502].includes(setup.status));
  const initializing = process.argv[2] === 'init';
  const wallet = { wallet_password: password };
  if (initializing) {
    const seed = await req('/api/lnd/wallet/genseed', { method: 'POST', headers: {
      'content-type': 'application/json', 'x-xsrf-token': decodeURIComponent(jar['XSRF-TOKEN']), authorization: 'Bearer ' + token
    }, body: '{}' });
    assert.equal(seed.status, 200, 'RTL seed generation failed');
    wallet.cipher_seed_mnemonic = (await seed.json()).cipher_seed_mnemonic;
  }
  const response = await req('/api/lnd/wallet/wallet/' + (initializing ? 'initwallet' : 'unlockwallet'), { method: 'POST', headers: {
    'content-type': 'application/json', 'x-xsrf-token': decodeURIComponent(jar['XSRF-TOKEN']), authorization: 'Bearer ' + token
  }, body: JSON.stringify(wallet) });
  assert.equal(response.status, 201, 'RTL wallet unlock failed');
  console.log(JSON.stringify({ operation: initializing ? 'init' : 'unlock', authenticatedRtlWalletOperation: true, verifiedLndTransport: true }));
})().catch(error => { console.error(error); process.exit(1); });
