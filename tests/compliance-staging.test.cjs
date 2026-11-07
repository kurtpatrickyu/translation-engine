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

test('checked-in inventory covers the exact diagnostic native/PYZ candidate', t => {
  const root = path.resolve(__dirname, '..');
  const inv = JSON.parse(fs.readFileSync(path.join(root, 'packaging/compliance-inventory.json')));
  s.validateInventory(inv);
  const auditPath = path.join(root, inv.candidate.audit.path);
  if (!fs.existsSync(auditPath)) return t.skip('Local diagnostic evidence is deliberately ignored; run candidate staging separately.');
  const result = s.verifyCandidate(root, inv);
  assert.equal(result.audit.file_count, 180); assert.equal(inv.candidate.third_party_roots.length, 17);
});
