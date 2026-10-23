const fs = require('node:fs');
const password = process.env.APP_PASSWORD;
if (!password || ['changeme', 'dappnode'].includes(password)) {
  console.error('Set APP_PASSWORD to a non-default password before starting RTL.');
  process.exit(1);
}
const config = JSON.parse(fs.readFileSync('/opt/dappnode/RTL-Config.json', 'utf8'));
// APP_PASSWORD is consumed by RTL itself. Do not interpolate it into JSON or share it with LND.
fs.mkdirSync('/RTL/backup/node-1/restore', { recursive: true });
fs.writeFileSync('/RTL/RTL-Config.json', JSON.stringify(config, null, 2) + '\n', { mode: 0o600 });
