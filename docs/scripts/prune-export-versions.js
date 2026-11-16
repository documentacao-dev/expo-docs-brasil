import fs from 'node:fs';
import path from 'node:path';
import semver from 'semver';

/**
 * Tradução: o `next build` exporta todas as versões da SDK (~1,1 GB em docs/out). Para o deploy
 * ficar menor, este script apaga de `out/versions/` o `unversioned` e as versões antigas
 * (vNN.N.N abaixo da mais nova). Ficam `latest` e a versão mais nova. Rode depois do `pnpm export`.
 */
const outVersions = path.join(import.meta.dirname, '..', 'out', 'versions');
const kept = new Set(['latest']);
const versionDirs = fs
  .readdirSync(outVersions, { withFileTypes: true })
  .filter(entry => entry.isDirectory())
  .map(entry => entry.name);
const numbered = versionDirs.filter(name => semver.valid(name)).sort(semver.rcompare);
if (numbered[0]) {
  kept.add(numbered[0]);
}

for (const name of versionDirs) {
  if (!kept.has(name)) {
    fs.rmSync(path.join(outVersions, name), { recursive: true, force: true });
    console.log(`removido out/versions/${name}`);
  }
}
