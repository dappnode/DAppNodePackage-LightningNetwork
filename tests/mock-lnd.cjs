// Synthetic read-only LND fixture. Its TLS key stays outside the volume mounted by RTL.
const https = require('node:https'), fs = require('node:fs');
const context = () => ({ key: fs.readFileSync('/tmp/lnd-fixture.key'), cert: fs.readFileSync('/tmp/lnd-fixture.crt') });
fs.writeFileSync('/shared/tls.cert', context().cert);
fs.writeFileSync('/shared/admin.macaroon', Buffer.from('deadbeef', 'hex'));
fs.writeFileSync('/shared/http-audit', '');
const server = https.createServer(context(), (q, s) => {
  fs.appendFileSync('/shared/http-audit', q.method + ' ' + q.url + '\n');
  s.setHeader('content-type', 'application/json');
  if (q.headers['grpc-metadata-macaroon'] !== 'deadbeef') { s.writeHead(401); return s.end('{}'); }
  let result;
  if (q.url === '/v1/getinfo') result = { identity_pubkey: '02' + 'ab'.repeat(32), alias: 'Node test fixture', version: '0.21.4-beta', num_active_channels: 0, num_peers: 0, synced_to_chain: false, synced_to_graph: false, chains: [{ chain: 'bitcoin', network: 'mainnet' }] };
  else if (q.url === '/v1/channels/backup') result = { single_chan_backups: { chan_backups: [] }, multi_chan_backup: { chan_points: [], multi_chan_backup: '' } };
  else if (q.url.startsWith('/v1/invoices')) result = { invoices: [] };
  else result = {};
  s.end(JSON.stringify(result));
}).listen(8080, '0.0.0.0');
process.on('SIGUSR2', () => server.setSecureContext(context()));
