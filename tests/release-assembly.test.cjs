'use strict';
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const s = require('../scripts/stage_compliance.cjs');
const r = require('../scripts/assemble_release.cjs');
const root = path.resolve(__dirname, '..');

test('ZIP output is byte-identical across entry order and has canonical metadata and CRC', () => {
  const entries = [['z/source.py', Buffer.from('source\r\n')], ['a/LICENSE', Buffer.from('original license')]];
  const a = r.zip(entries), b = r.zip([...entries].reverse());
  assert.deepEqual(a, b);
  const contents = s.zipMembers(a);
  assert.deepEqual([...contents.keys()], ['a/LICENSE', 'z/source.py']);
  assert.equal(contents.get('z/source.py')().toString(), 'source\r\n');
  assert.equal(a.readUInt16LE(10), 0); assert.equal(a.readUInt16LE(12), 33);
  assert.equal(r.crc32(Buffer.from('123456789')), 0xcbf43926);
});

test('archives reject models, download caches, virtual environments, logs, traversal and case collisions', () => {
  for (const file of ['model.onnx', 'model.argosmodel', 'downloads/LICENSE', '.venv/python.exe', 'runtime.log', '../escape'])
    assert.throws(() => r.zip([[file, Buffer.from('content')]]));
  assert.throws(() => r.zip([['A/LICENSE', Buffer.from('a')], ['a/license', Buffer.from('b')]]), /Duplicate ZIP/);
});

function workerFixture(extra = []) {
  const entries = [['translation-engine-worker/translation-engine-worker.exe', Buffer.from('worker')],
    ['translation-engine-worker/_internal/python312.dll', Buffer.from('python')],
    ['translation-engine-worker/_internal/numpy.libs/msvcp140-wheel.dll', Buffer.from('numpy runtime')], ...extra];
  const worker_files = entries.map(([name, b]) => ({name, bytes: b.length, sha256: s.hash(b)}));
  const audit = {all_file_sha256: Object.fromEntries(entries.slice(0, 3).map(([f, b]) => [f.split('/').slice(1).join('/'), s.hash(b)]))};
  return {entries, manifest: {worker_files}, audit};
}

test('complete worker coverage preserves all original hashes and NumPy dependency', () => {
  const f = workerFixture();
  r.validateWorker(r.zip(f.entries), f.manifest, f.audit);
  assert.throws(() => r.validateWorker(r.zip(f.entries.slice(1)), f.manifest, f.audit), /coverage/);
  f.entries[0][1] = Buffer.from('tampered');
  assert.throws(() => r.validateWorker(r.zip(f.entries), f.manifest, f.audit));
});

test('ordinary VC DLLs cannot reappear even if listed with self-consistent hashes', () => {
  for (const name of ['MSVCP140.dll', 'msvcp140_1.dll', 'vcruntime140.dll', 'VCRUNTIME140_1.DLL']) {
    const f = workerFixture([['translation-engine-worker/_internal/' + name, Buffer.from('forbidden')]]);
    assert.throws(() => r.validateWorker(r.zip(f.entries), f.manifest, f.audit));
  }
});

test('real candidate manifest, archive, source commit and artifact hashes agree', t => {
  const final = path.join(root, 'candidate-staging/worker-0.1.0-rc.1-final');
  const directory = fs.existsSync(final) ? final : path.join(root, 'candidate-staging/worker-0.1.0-rc.1');
  if (!fs.existsSync(directory)) return t.skip('Generate local candidate for integration coverage.');
  const m = JSON.parse(fs.readFileSync(path.join(directory, 'manifest.json')));
  r.validateManifest(m);
  const cfg = require('../packaging/release-candidate.json');
  assert.equal(m.source.commit, cfg.source_commit);
  assert.equal(m.source.materials_commit, cfg.materials_commit);
  assert.equal(m.publication.release_ready, false);
  // Current docs/tool bytes must not force rewriting the immutable candidate.
  assert.deepEqual(r.assemble(root, path.join(root, 'packaging/release-candidate.json'), directory, true), m);
  const fresh = r.prepare(root, path.join(root, 'packaging/release-candidate.json'));
  r.validateWorker(fresh.payload.get('translation-engine-worker-win-x64.zip'), fresh.manifest, fresh.audit);
  assert(fresh.payload.get('WINDOWS-CANDIDATE.md').equals(fs.readFileSync(path.join(root, 'README.md'))));
  for (const file of ['README.md', 'docs/development.md', 'docs/protocol-v1.md', 'docs/releasing.md', 'docs/troubleshooting.md']) {
    assert(fresh.workerEntries.has('translation-engine-worker/release-info/' + file));
    assert(fresh.sources.has('assembly/' + file));
  }
  assert.equal(m.baseline.executable_sha256, 'ec06bf07399b9d96d140e2c828772666aa12124b8991a2d622ebca52ced79d7d');
  for (const a of m.artifacts) {
    const b = s.pinned(path.join(directory, a.name), a.sha256); assert.equal(b.length, a.bytes);
  }
  r.validateWorker(fs.readFileSync(path.join(directory, 'translation-engine-worker-win-x64.zip')), m,
    require('../build/diagnostic-20261107-211131/native-static-audit.json'));
  const sources = s.zipMembers(fs.readFileSync(path.join(directory, 'translation-engine-corresponding-source.zip')));
  const sourceCommit = JSON.parse(sources.get('SOURCE_COMMIT.json')());
  assert.equal(sourceCommit.commit, m.source.commit);
  for (const file of ['repository/packaging/worker.spec', 'sources/minisbd/minisbd-0.9.5.tar.gz',
    'sources/tqdm/tqdm-4.70.1.tar.gz', 'sources/worker/requirements.lock', 'sources/worker/scripts/build_argos_wheel.py'])
    assert(sources.has(file), file);
  const compliance = s.zipMembers(fs.readFileSync(path.join(directory, 'translation-engine-compliance.zip')));
  assert(compliance.has('BLOCKERS.txt')); assert(compliance.has('SOURCE_AVAILABILITY.md'));
  assert([...compliance.keys()].some(f => f.startsWith('licenses/minisbd/')));
  for (const f of [...sources.keys(), ...compliance.keys()]) assert(!r.forbidden(f), f);
  for (const mutate of [m => { m.source.commit = 'main'; }, m => { m.publication.release_ready = true; },
    m => { m.artifacts[0].sha256 = 'unknown'; }, m => { m.artifacts.push(m.artifacts[0]); },
    m => { m.external_models[0].bundled = true; }, m => { m.unreviewed = true; }]) {
    const changed = structuredClone(m); mutate(changed); assert.throws(() => r.validateManifest(changed));
  }
});

test('candidate verification rejects missing, extra and tampered outputs including rewritten metadata', t => {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'release-output-'));
  t.after(() => fs.rmSync(temp, {recursive: true, force: true}));
  const expected = new Map([['manifest.json', Buffer.from('{"source_commit":"matching"}')], ['worker.zip', Buffer.from('worker bytes')]]);
  for (const [name, bytes] of expected) fs.writeFileSync(path.join(temp, name), bytes);
  r.verifyFiles(temp, expected);
  fs.writeFileSync(path.join(temp, 'manifest.json'), '{"source_commit":"substituted"}');
  assert.throws(() => r.verifyFiles(temp, expected), /Candidate differs/);
  fs.writeFileSync(path.join(temp, 'manifest.json'), expected.get('manifest.json'));
  fs.unlinkSync(path.join(temp, 'worker.zip'));
  assert.throws(() => r.verifyFiles(temp, expected), /coverage/);
  fs.writeFileSync(path.join(temp, 'worker.zip'), expected.get('worker.zip'));
  fs.writeFileSync(path.join(temp, 'extra.onnx'), 'unexpected');
  assert.throws(() => r.verifyFiles(temp, expected), /coverage/);
});

test('missing, mismatched and tampered evidence fails before assembly writes', t => {
  const cfg = require('../packaging/release-candidate.json');
  if (!fs.existsSync(path.join(root, cfg.compliance_directory))) return t.skip('Local compliance dossier not available.');
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'release-input-'));
  t.after(() => fs.rmSync(temp, {recursive: true, force: true}));
  const configPath = path.join(temp, 'config.json');
  for (const mutate of [c => { c.source_commit = 'a'.repeat(40); },
    c => { c.regression_evidence[0].sha256 = 'f'.repeat(64); },
    c => { c.regression_evidence[0].path = 'build/missing-release-evidence.json'; },
    c => { c.models.translation.sha256 = '0'.repeat(64); },
    c => { c.compliance_manifest_sha256 = '0'.repeat(64); }]) {
    const changed = structuredClone(cfg); mutate(changed); fs.writeFileSync(configPath, s.json(changed));
    assert.throws(() => r.prepare(root, configPath));
  }
});
