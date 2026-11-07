'use strict';
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const s = require('../scripts/stage_compliance.cjs');

function fixture(t) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'compliance-test-'));
  t.after(() => fs.rmSync(root, {recursive: true, force: true}));
  function write(name, value) {
    const file = path.join(root, name); fs.mkdirSync(path.dirname(file), {recursive: true});
    fs.writeFileSync(file, typeof value === 'string' ? value : s.json(value));
    return {path: name, sha256: s.hash(fs.readFileSync(file))};
  }
  const worker = write('dist/worker/worker.exe', 'verified executable');
  const license = write('supplier/LICENSE', 'Unmodified supplier license\r\n');
  const toc = write('build/PYZ.toc', "[('minisbd', 'source/minisbd.py', 'PYMODULE')]\n");
  const input = write('src/entry.py', 'print(42)\n');
  const build = write('build/build.json', {passed: true, source_sha256: {[input.path]: input.sha256}});
  const audit = write('build/audit.json', {passed: true, errors: [], file_count: 1,
    exe_sha256: worker.sha256, zip_sha256: 'a'.repeat(64), all_file_sha256: {'worker.exe': worker.sha256}});
  const inventory = {schema_version: 1, scope: 'preparatory-only',
    candidate: {worker: 'dist/worker', audit, build, pyz: toc, exe_sha256: worker.sha256,
      zip_sha256: 'a'.repeat(64), pyz_roots: ['minisbd'], third_party_roots: ['minisbd']},
    obligations: [{id: 'agpl-scope', status: 'blocked', blocker: 'AGPL scope not approved'}],
    components: [{id: 'minisbd', name: 'MiniSBD', version: '0.9.5', redistributed_form: 'bytecode', license: 'AGPLv3',
      matching_source_required: 'yes', source_identity: {}, status: 'verified', blockers: [],
      pyz_roots: ['minisbd'], worker_files: ['worker.exe'], materials: [{kind: 'license', required: true,
        destination: 'licenses/minisbd/LICENSE', source: license}]}]};
  const inventoryPath = path.join(root, 'inventory.json');
  const save = () => write('inventory.json', inventory);
  save();
  return {root, write, inventory, inventoryPath, save, output: path.join(root, 'candidate-staging/one')};
}

test('stages deterministically, preserves supplier bytes and worker; blocked readiness', t => {
  const f = fixture(t), before = fs.readFileSync(path.join(f.root, 'dist/worker/worker.exe'));
  const a = s.stage(f.root, f.inventoryPath, f.output);
  const second = path.join(f.root, 'candidate-staging/two');
  const b = s.stage(f.root, f.inventoryPath, second);
  assert.deepEqual(a, b); assert.equal(a.release_ready, false); assert.equal(a.compliance_ready, false);
  assert.ok(a.blockers.some(b => b.id === 'agpl-scope'));
  for (const name of s.walk(f.output)) assert.deepEqual(fs.readFileSync(path.join(f.output, name)), fs.readFileSync(path.join(second, name)));
  assert.deepEqual(fs.readFileSync(path.join(f.output, 'licenses/minisbd/LICENSE')), fs.readFileSync(path.join(f.root, 'supplier/LICENSE')));
  assert.deepEqual(before, fs.readFileSync(path.join(f.root, 'dist/worker/worker.exe')));
  assert.throws(() => s.stage(f.root, f.inventoryPath, f.output), /already exists/);
});

test('inventory requires one owner per frozen file and all known distribution roots', t => {
  const f = fixture(t); f.inventory.components[0].worker_files = []; f.save();
  assert.throws(() => s.verifyCandidate(f.root, f.inventory), /cover exact worker/);
  f.inventory.components[0].worker_files = ['worker.exe']; f.inventory.components[0].pyz_roots = []; f.save();
  assert.throws(() => s.verifyCandidate(f.root, f.inventory), /Missing\/duplicate frozen/);
});

test('notice index is stable for multiple supplier texts in archive order', t => {
  const f = fixture(t), p = f.write('supplier/NOTICE', 'supplier attribution');
  f.inventory.components[0].materials.push({source: p, destination: 'licenses/minisbd/AAA-NOTICE', kind: 'notice', required: true});
  f.save(); s.stage(f.root, f.inventoryPath, f.output); s.verifyStage(f.root, f.inventoryPath, f.output);
});

test('unrecorded or changed worker file fails before staging writes', t => {
  const f = fixture(t); f.write('dist/worker/extra.dll', 'extra');
  assert.throws(() => s.stage(f.root, f.inventoryPath, f.output), /inventory differs/);
  assert.equal(fs.existsSync(f.output), false);
  fs.unlinkSync(path.join(f.root, 'dist/worker/extra.dll')); f.write('dist/worker/worker.exe', 'tampered');
  assert.throws(() => s.stage(f.root, f.inventoryPath, f.output), /SHA-256 mismatch/);
});

test('missing required license or unverified hash is recorded as blocking, never ready', t => {
  const f = fixture(t); fs.unlinkSync(path.join(f.root, 'supplier/LICENSE'));
  const a = s.stage(f.root, f.inventoryPath, f.output);
  assert.equal(a.components[0].status, 'incomplete');
  assert.ok(a.blockers.some(b => b.id === 'material:licenses/minisbd/LICENSE'));
  assert.equal(a.compliance_ready, false); s.verifyStage(f.root, f.inventoryPath, f.output);
  f.write('supplier/LICENSE', 'unexpected new text');
  const b = s.stage(f.root, f.inventoryPath, path.join(f.root, 'candidate-staging/changed'));
  assert.ok(b.blockers.some(b => b.reason.includes('SHA-256 mismatch')));
});

test('missing/tampered staged licenses or checksum lists fail integrity verification', t => {
  const f = fixture(t); s.stage(f.root, f.inventoryPath, f.output);
  fs.writeFileSync(path.join(f.output, 'licenses/minisbd/LICENSE'), 'changed');
  assert.throws(() => s.verifyStage(f.root, f.inventoryPath, f.output), /SHA-256 mismatch/);
  fs.copyFileSync(path.join(f.root, 'supplier/LICENSE'), path.join(f.output, 'licenses/minisbd/LICENSE'));
  fs.unlinkSync(path.join(f.output, 'licenses/minisbd/LICENSE'));
  assert.throws(() => s.verifyStage(f.root, f.inventoryPath, f.output), /inventory differs/);
  fs.copyFileSync(path.join(f.root, 'supplier/LICENSE'), path.join(f.output, 'licenses/minisbd/LICENSE'));
  fs.writeFileSync(path.join(f.output, 'SHA256SUMS'), 'bad');
  assert.throws(() => s.verifyStage(f.root, f.inventoryPath, f.output), /SHA256SUMS differs/);
});

test('readiness flag edits cannot promote preparatory output', t => {
  const f = fixture(t); s.stage(f.root, f.inventoryPath, f.output);
  const file = path.join(f.output, 'manifest.json'), m = JSON.parse(fs.readFileSync(file));
  m.release_ready = true; fs.writeFileSync(file, s.json(m));
  assert.throws(() => s.verifyStage(f.root, f.inventoryPath, f.output), /cannot declare readiness/);
});

test('rewriting a staged license and its manifest hash cannot replace pinned license material', t => {
  const f = fixture(t); s.stage(f.root, f.inventoryPath, f.output);
  const file = path.join(f.output, 'manifest.json'), m = JSON.parse(fs.readFileSync(file));
  const record = m.files.find(f => f.path === 'licenses/minisbd/LICENSE');
  fs.writeFileSync(path.join(f.output, record.path), 'substituted license');
  record.sha256 = s.hash(Buffer.from('substituted license')); record.bytes = 19;
  fs.writeFileSync(file, s.json(m));
  assert.throws(() => s.verifyStage(f.root, f.inventoryPath, f.output), /mismatched material/);
});

test('external models, traversal, worker destination and extra staged files are rejected', t => {
  const f = fixture(t);
  assert.throws(() => s.stage(f.root, f.inventoryPath, path.join(f.root, 'dist/overwrite')), /below candidate-staging/);
  assert.throws(() => s.safe(f.root, '../escape'), /Unsafe relative/);
  f.write('dist/worker/model.ONNX', 'model');
  assert.throws(() => s.verifyCandidate(f.root, f.inventory), /inventory differs/);
  fs.unlinkSync(path.join(f.root, 'dist/worker/model.ONNX'));
  f.inventory.components[0].materials[0].destination = 'sources/external.argosmodel'; f.save();
  assert.throws(() => s.stage(f.root, f.inventoryPath, f.output), /Invalid material/);
  f.inventory.components[0].materials[0].destination = 'licenses/minisbd/LICENSE'; f.save(); s.stage(f.root, f.inventoryPath, f.output);
  fs.writeFileSync(path.join(f.output, 'extra.onnx'), 'model');
  assert.throws(() => s.verifyStage(f.root, f.inventoryPath, f.output), /inventory differs/);
});

function storedZip(name, data) {
  const filename = Buffer.from(name), bytes = Buffer.from(data), local = Buffer.alloc(30), central = Buffer.alloc(46), end = Buffer.alloc(22);
  local.writeUInt32LE(0x04034b50); local.writeUInt32LE(bytes.length, 18); local.writeUInt32LE(bytes.length, 22); local.writeUInt16LE(filename.length, 26);
  central.writeUInt32LE(0x02014b50); central.writeUInt32LE(bytes.length, 20); central.writeUInt32LE(bytes.length, 24); central.writeUInt16LE(filename.length, 28);
  end.writeUInt32LE(0x06054b50); end.writeUInt16LE(1, 8); end.writeUInt16LE(1, 10); end.writeUInt32LE(central.length + filename.length, 12); end.writeUInt32LE(local.length + filename.length + bytes.length, 16);
  return Buffer.concat([local, filename, bytes, central, filename, end]);
}
test('ZIP reader rejects model-containing whole archives and unsafe members', () => {
  assert.throws(() => s.zipMembers(storedZip('data/model.onnx', 'binary')), /External model/);
  assert.throws(() => s.zipMembers(storedZip('../LICENSE', 'text')), /Unsafe relative/);
  assert.equal(s.zipMembers(storedZip('LICENSE', 'unaltered text')).get('LICENSE')().toString(), 'unaltered text');
  // A wheel may contain unselected datasets; they may never be staged as members.
  assert.equal(s.zipMembers(storedZip('data/model.onnx', 'binary'), true).size, 1);
});

test('changed build source invalidates source correspondence', t => {
  const f = fixture(t); f.write('src/entry.py', 'changed');
  assert.throws(() => s.verifyCandidate(f.root, f.inventory), /SHA-256 mismatch/);
});

test('checked-in inventory covers the latest post-003 native/PYZ candidate', t => {
  const root = path.resolve(__dirname, '..');
  const inv = JSON.parse(fs.readFileSync(path.join(root, 'packaging/compliance-inventory.json')));
  s.validateInventory(inv);
  const auditPath = path.join(root, inv.candidate.audit.path);
  if (!fs.existsSync(auditPath)) return t.skip('Local diagnostic evidence is deliberately ignored; run candidate staging separately.');
  const result = s.verifyCandidate(root, inv);
  assert.equal(result.audit.file_count, 176); assert.equal(result.audit.pe_count, 49);
  assert.equal(inv.candidate.third_party_roots.length, 17);
  assert.match(inv.candidate.worker, /diagnostic-20261107-211131/);
  assert.equal(inv.candidate.exe_sha256, 'ec06bf07399b9d96d140e2c828772666aa12124b8991a2d622ebca52ced79d7d');
});

test('MiniSBD and tqdm exact publisher sources match locked wheel Python bytes', () => {
  const root = path.resolve(__dirname, '..'), inv = require('../packaging/compliance-inventory.json');
  for (const id of ['minisbd', 'tqdm']) {
    const c = inv.components.find(c => c.id === id);
    const archive = c.materials.find(m => m.kind === 'source-archive');
    const tar = s.tarMembers(s.pinned(path.join(root, archive.source.path), c.source_identity.sdist_sha256));
    const wheelPath = path.join(root, c.source_identity.wheel);
    if (!fs.existsSync(wheelPath)) continue; // Cached wheel is optional in a source-only checkout.
    const wheel = s.zipMembers(s.pinned(wheelPath, c.source_identity.wheel_sha256), true);
    const members = [...wheel.keys()].filter(n => n.startsWith(id + '/') && n.endsWith('.py')).sort();
    assert.deepEqual(members, [...c.source_identity.wheel_source_members].sort());
    if (id === 'minisbd') assert.equal(members.length, 9);
    for (const member of members) assert.deepEqual(wheel.get(member)(), tar.get(id + '-' + c.version + '/' + member)());
  }
});

test('required original texts, attributions and unresolved native obligations stay mapped', () => {
  const root = path.resolve(__dirname, '..'), inv = require('../packaging/compliance-inventory.json');
  for (const id of ['argostranslate', 'minisbd', 'tqdm', 'ctranslate2', 'sentencepiece', 'numpy', 'onnxruntime', 'python', 'pyinstaller']) {
    const c = inv.components.find(c => c.id === id);
    assert.ok(c.materials.some(m => /license|notice/.test(m.kind)), id);
  }
  for (const c of inv.components) for (const m of c.materials.filter(m => m.source.path?.startsWith('LICENSES/'))) {
    const bytes = s.pinned(path.join(root, m.source.path), m.source.sha256);
    if (m.provenance?.sha256) assert.equal(s.hash(bytes), m.provenance.sha256);
    if (m.provenance?.member && m.provenance.path && fs.existsSync(path.join(root, m.provenance.path))) {
      const origin = s.pinned(path.join(root, m.provenance.path), m.provenance.archive_sha256);
      const archive = /\.tar\.gz$/.test(m.provenance.path) ? s.tarMembers(origin) : s.zipMembers(origin, true);
      assert.deepEqual(bytes, archive.get(m.provenance.member)());
    }
  }
  const mini = inv.components.find(c => c.id === 'minisbd');
  const texts = mini.materials.filter(m => m.source.path?.startsWith('LICENSES/'))
    .map(m => fs.readFileSync(path.join(root, m.source.path), 'utf8')).join('\n');
  for (const term of ['GNU AFFERO GENERAL PUBLIC LICENSE', 'Stanza NLP', 'Stanford Junior University', 'Apache License']) assert.ok(texts.includes(term), term);
  assert.ok(inv.components.find(c => c.id === 'tqdm').materials.some(m => m.source.path?.endsWith('MPL-2.0.txt')));
  for (const id of ['intel-openmp', 'msvc-numpy', 'ct2-static', 'sentencepiece-static', 'ort-static', 'openblas'])
    assert.ok(inv.components.find(c => c.id === id).blockers.length, id);
  assert.ok(inv.obligations.some(o => o.id === 'source-delivery'));
  assert.equal(inv.components.some(c => c.id === 'msvc'), false);
  const ordinary = /\/(msvcp140(?:_1)?|vcruntime140(?:_1)?)\.dll$/i;
  assert.equal(inv.components.some(c => c.worker_files.some(f => ordinary.test(f))), false);
  assert.ok(inv.components.find(c => c.id === 'msvc-numpy').worker_files.length);
  assert.ok(inv.candidate.external_prerequisites.every(p => p.bundled === false));
});

test('recipient source instructions are pinned, including immutable release delivery', t => {
  const f = fixture(t);
  const source = f.write('SOURCE_AVAILABILITY.md', 'Source accompanies this executable.\n');
  f.inventory.components[0].materials.push({source, destination: 'sources/worker/SOURCE_AVAILABILITY.md', kind: 'build-instructions', required: true});
  f.save(); s.stage(f.root, f.inventoryPath, f.output);
  fs.writeFileSync(path.join(f.output, 'SOURCE_AVAILABILITY.md'), 'moving branch only');
  assert.throws(() => s.verifyStage(f.root, f.inventoryPath, f.output), /SHA-256 mismatch/);
});

test('current documentation can change while archived candidate instructions remain hash pinned', t => {
  const f = fixture(t);
  const original = 'Original candidate build instructions.\r\n';
  const source = f.write('docs/development.md', original);
  f.write('packaging/sources/candidate-documentation/docs/development.md', original);
  f.inventory.components[0].materials.push({source,
    destination: 'sources/worker/docs/development.md', kind: 'build-instructions', required: true});
  f.save();
  f.write('docs/development.md', 'Current developer guide.\n');
  s.stage(f.root, f.inventoryPath, f.output);
  assert.equal(fs.readFileSync(path.join(f.output, 'sources/worker/docs/development.md'), 'utf8'), original);
  s.verifyStage(f.root, f.inventoryPath, f.output);
  f.write('packaging/sources/candidate-documentation/docs/development.md', 'tampered');
  const m = s.stage(f.root, f.inventoryPath, path.join(f.root, 'candidate-staging/tampered'));
  assert(m.blockers.some(b => b.id === 'material:sources/worker/docs/development.md'));
});

test('documentation archive cannot substitute runtime inputs or supplier licenses', t => {
  const f = fixture(t);
  f.write('packaging/sources/candidate-documentation/supplier/LICENSE', 'Unmodified supplier license\r\n');
  f.write('supplier/LICENSE', 'tampered');
  const m = s.stage(f.root, f.inventoryPath, f.output);
  assert(m.blockers.some(b => b.id === 'material:licenses/minisbd/LICENSE'));
  f.write('supplier/LICENSE', 'Unmodified supplier license\r\n');
  f.write('packaging/sources/candidate-documentation/src/entry.py', 'print(42)\n');
  f.write('src/entry.py', 'tampered');
  assert.throws(() => s.verifyCandidate(f.root, f.inventory), /SHA-256 mismatch/);
});

function sourceTar(name) {
  const h = Buffer.alloc(512), payload = Buffer.from('source');
  h.write(name); h.write('0000644\0', 100); h.write('0000006\0', 124); h[156] = 48;
  h.fill(32, 148, 156);
  const sum = [...h].reduce((a, b) => a + b, 0);
  h.write(sum.toString(8).padStart(6, '0') + '\0 ', 148);
  return require('node:zlib').gzipSync(Buffer.concat([h, payload, Buffer.alloc(512 - payload.length + 1024)]));
}

test('source tarballs reject model binaries, traversal and invalid headers', () => {
  assert.equal(s.tarMembers(sourceTar('package/source.py')).get('package/source.py')().toString(), 'source');
  assert.throws(() => s.tarMembers(sourceTar('package/model.onnx')), /External model/);
  assert.throws(() => s.tarMembers(sourceTar('../escape.py')), /Unsafe relative/);
  const zlib = require('node:zlib'), bytes = zlib.gunzipSync(sourceTar('package/source.py'));
  bytes[10] ^= 1;
  assert.throws(() => s.tarMembers(zlib.gzipSync(bytes)), /Tar checksum/);
});

test('frozen-source evidence cannot be substituted or omit staged preferred source', t => {
  const f = fixture(t);
  const report = {passed: true, exe_sha256: f.inventory.candidate.exe_sha256,
    records: [{component: 'minisbd', module: 'minisbd', matches: true, source_sha256: 'a'.repeat(64),
      source: {path: 'wheel.whl', member: 'minisbd/__init__.py', archive_sha256: 'b'.repeat(64)}}]};
  f.inventory.candidate.source_correspondence = f.write('build/correspondence.json', report); f.save();
  assert.throws(() => s.stage(f.root, f.inventoryPath, f.output), /Unstaged\/stale matching source/);
  report.exe_sha256 = 'c'.repeat(64);
  f.inventory.candidate.source_correspondence = f.write('build/correspondence.json', report); f.save();
  assert.throws(() => s.verifyCandidate(f.root, f.inventory), /Frozen-source correspondence failed/);
});
