const assert = require("node:assert/strict");
const fs = require("node:fs");
const dns = require("node:dns");
const { X509Certificate, createHash } = require("node:crypto");
const { rootCertificates } = require("node:tls");
const expected = process.argv[2] || "22.23.4";
assert.equal(process.versions.node, expected);
assert.throws(() => dns.resolve4("example.com\0.invalid", () => {}), { code: "ERR_INVALID_ARG_VALUE" });
const blocked = new Set([
  "bd153ed7b0434f6886b17bce8bbe84ed340c7132d702a8f4fa318f756ecbd6f3",
  "c619e4780ed8e0abeda24ad732567de4383a7ea941338f6d1a7d1b49ac792fe9",
  "8d417db2dd8bf5e3084d1e3f196d583849d81bdd4c00c70b9d39369e96b8c782"
]);
const systemRoots = fs.readFileSync(process.argv[3] || "/etc/ssl/certs/ca-certificates.crt", "utf8")
  .match(/-----BEGIN CERTIFICATE-----[\s\S]*?-----END CERTIFICATE-----/g);
assert.ok(systemRoots.length > 100);
for (const pem of [...rootCertificates, ...systemRoots]) {
  const key = new X509Certificate(pem).publicKey.export({ type: "spki", format: "der" });
  assert.ok(!blocked.has(createHash("sha256").update(key).digest("hex")));
}
console.log(JSON.stringify({ node: process.versions.node, systemRoots: systemRoots.length,
  nodeRoots: rootCertificates.length, dnsNulRejected: true, distrustedRootsAbsent: true }));
