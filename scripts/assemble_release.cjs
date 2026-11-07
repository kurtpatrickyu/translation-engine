/* Local worker candidate assembly only. Node >=22, no npm dependencies. */
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const cp = require('node:child_process');
const zlib = require('node:zlib');
const assert = require('node:assert/strict');
const s = require('./stage_compliance.cjs');
const ROOT = path.resolve(__dirname, '..');
const REPO = 'https://github.com/kurtpatrickyu/translation-engine';
const WORKER = 'translation-engine-worker-win-x64.zip';
const COMPLIANCE = 'translation-engine-compliance.zip';
const SOURCE = 'translation-engine-corresponding-source.zip';
const excludedVC = /^(msvcp140(?:_1)?|vcruntime140(?:_1)?)\.dll$/i;
const forbidden = name => /\.(onnx|argosmodel|pyc|pyo|log)$/i.test(name) ||
  name.split('/').some(p => /^(downloads|\.venv|venv|model-cache|__pycache__)$/i.test(p)) ||
  /^vc_?redist/i.test(path.posix.basename(name));
const crcTable = Array.from({length: 256}, (_, n) => {
  for (let k = 0; k < 8; k++) n = n & 1 ? 0xedb88320 ^ (n >>> 1) : n >>> 1;
  return n >>> 0;
});
function crc32(bytes) {
  let n = 0xffffffff;
  for (const b of bytes) n = crcTable[(n ^ b) & 255] ^ (n >>> 8);
  return (n ^ 0xffffffff) >>> 0;
}

// Canonical ZIP: sorted paths, UTF-8, DOS 1980-01-01, fixed permissions,
// no extra fields/comments, deterministic raw DEFLATE. No binary changes.
function zip(entries) {
  const chunks = [], directory = [], names = new Set(); let offset = 0;
  for (const [name, bytes] of [...entries].sort(([a], [b]) => a < b ? -1 : 1)) {
    s.safe(ROOT, name); assert(!forbidden(name), 'Forbidden release member: ' + name);
    assert(!names.has(name.toLowerCase()), 'Duplicate ZIP path'); names.add(name.toLowerCase());
    const filename = Buffer.from(name), packed = zlib.deflateRawSync(bytes, {level: 9});
    const crc = crc32(bytes), local = Buffer.alloc(30), central = Buffer.alloc(46);
    local.writeUInt32LE(0x04034b50); local.writeUInt16LE(20, 4); local.writeUInt16LE(0x800, 6);
    local.writeUInt16LE(8, 8); local.writeUInt16LE(33, 12); local.writeUInt32LE(crc, 14);
    local.writeUInt32LE(packed.length, 18); local.writeUInt32LE(bytes.length, 22); local.writeUInt16LE(filename.length, 26);
    central.writeUInt32LE(0x02014b50); central.writeUInt16LE(0x314, 4); central.writeUInt16LE(20, 6);
    central.writeUInt16LE(0x800, 8); central.writeUInt16LE(8, 10); central.writeUInt16LE(33, 14);
    central.writeUInt32LE(crc, 16); central.writeUInt32LE(packed.length, 20); central.writeUInt32LE(bytes.length, 24);
    central.writeUInt16LE(filename.length, 28); central.writeUInt32LE(0x81a40000, 38); central.writeUInt32LE(offset, 42);
    chunks.push(local, filename, packed); directory.push(central, filename);
    offset += local.length + filename.length + packed.length;
  }
  assert(names.size < 65535 && offset < 0xffffffff, 'ZIP64 not supported');
  const central = Buffer.concat(directory), end = Buffer.alloc(22);
  end.writeUInt32LE(0x06054b50); end.writeUInt16LE(names.size, 8); end.writeUInt16LE(names.size, 10);
  end.writeUInt32LE(central.length, 12); end.writeUInt32LE(offset, 16);
  return Buffer.concat([...chunks, central, end]);
}
function git(root, args) {
  return cp.execFileSync('git', ['-c', 'safe.directory=' + root.replaceAll('\\', '/'), ...args],
    {cwd: root, maxBuffer: 128 * 1024**2, windowsHide: true});
}
function exactKeys(value, keys, label) {
  assert.deepEqual(Object.keys(value).sort(), [...keys].sort(), 'Unexpected/missing ' + label + ' fields');
}
function validateManifest(m) {
  exactKeys(m, ['schema_version', 'candidate_id', 'worker_version', 'protocol_version', 'platform', 'architecture',
    'source', 'publication', 'baseline', 'backend', 'dependencies', 'external_prerequisites', 'external_models',
    'artifacts', 'worker_files', 'evidence', 'compliance', 'blockers', 'assembly'], 'manifest');
  assert.equal(m.schema_version, 1); assert.equal(m.platform, 'windows'); assert.equal(m.architecture, 'x64');
  assert.equal(m.protocol_version, 1); assert.match(m.worker_version, /^\d+\.\d+\.\d+$/);
  assert.equal(m.candidate_id, m.worker_version + '-rc.1');
  for (const key of ['commit', 'materials_commit']) assert.match(m.source[key], /^[a-f0-9]{40}$/);
  assert.equal(m.source.url, REPO + '/tree/' + m.source.commit);
  assert.deepEqual(m.publication, {status: 'local-candidate', tag: null, release_url: null, release_ready: false});
  assert.equal(m.backend, 'argos'); assert(m.dependencies.length >= 17);
  assert.equal(new Set(m.dependencies.map(c => c.id)).size, m.dependencies.length);
  for (const p of m.external_prerequisites) assert(p.bundled === false && /^https:\/\//.test(p.url));
  for (const a of m.external_models) {
    assert.equal(a.bundled, false); assert.match(a.source, /^https:\/\//); assert.match(a.sha256, /^[a-f0-9]{64}$/);
    assert(Number.isSafeInteger(a.bytes) && a.bytes > 0);
  }
  assert.equal(m.external_models.length, 2); assert.equal(m.compliance.ready, false); assert(m.blockers.length > 0);
  assert(!Object.hasOwn(m, 'sha256'), 'Manifest must not hash itself');
  const seen = new Set();
  for (const a of m.artifacts) {
    exactKeys(a, ['name', 'bytes', 'sha256', 'role'], 'artifact');
    assert.match(a.name, /^[A-Za-z0-9._-]+$/); assert(!forbidden(a.name));
    assert(!seen.has(a.name.toLowerCase()), 'Duplicate artifact'); seen.add(a.name.toLowerCase());
    assert.match(a.sha256, /^[a-f0-9]{64}$/); assert(Number.isSafeInteger(a.bytes) && a.bytes > 0);
  }
  assert.deepEqual([...seen].sort(), [WORKER, COMPLIANCE, SOURCE, 'WINDOWS-CANDIDATE.md', 'verify-checksums.ps1', 'manifest.schema.json'].map(n => n.toLowerCase()).sort());
  return m;
}
function outputPath(root, output) {
  const relative = path.relative(root, path.resolve(output)).replaceAll('\\', '/');
  assert(relative.startsWith('candidate-staging/'), 'Output must be below candidate-staging/');
  return s.safe(root, relative);
}
function prepare(root, configPath) {
  const cfg = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  const invPath = s.safe(root, 'packaging/compliance-inventory.json');
  const inv = JSON.parse(fs.readFileSync(invPath, 'utf8'));
  const candidate = s.verifyCandidate(root, inv);
  const complianceDir = s.safe(root, cfg.compliance_directory);
  const compliance = s.verifyStage(root, invPath, complianceDir);
  s.pinned(path.join(complianceDir, 'manifest.json'), cfg.compliance_manifest_sha256);
  assert(!compliance.blockers.some(b => b.id.startsWith('material:')), 'Missing required compliance material');
  assert.equal(cfg.source_commit, inv.components.find(c => c.id === 'translation-engine').source_identity.build_source_commit);
  assert.equal(git(root, ['rev-parse', cfg.source_commit]).toString().trim(), cfg.source_commit);
  assert.equal(git(root, ['rev-parse', cfg.materials_commit]).toString().trim(), cfg.materials_commit);
  // Byte pins above bind exact original inputs; Git comparison additionally
  // proves the public commit contains the matching runtime/build text (Git EOL rules apply).
  const inputs = Object.keys(candidate.build.source_sha256).filter(f => f !== 'packaging/compliance-inventory.json');
  git(root, ['diff', '--exit-code', cfg.source_commit, '--', ...inputs]);
  git(root, ['diff', '--exit-code', cfg.source_commit, cfg.materials_commit, '--', ...inputs]);
  const evidence = cfg.regression_evidence.map(e => {
    const r = JSON.parse(s.pinned(s.safe(root, e.path), e.sha256));
    assert.equal(r.worker_exe_sha256, inv.candidate.exe_sha256, 'Regression executable mismatch');
    assert.equal(r.worker_zip_sha256, inv.candidate.zip_sha256, 'Regression ZIP mismatch');
    assert.equal(r.functional_smoke_passed, true, 'Failed functional regression');
    assert.equal(r.info.engine_version, cfg.worker_version, 'Worker version differs');
    assert.equal(r.info.protocol_version, 1); assert.equal(r.info.backend, 'argos');
    assert.equal(r.model_sha256, cfg.models.translation.sha256);
    assert.equal(r.sbd_sha256, cfg.models.sentence_boundary.sha256);
    if (e.kind === 'unicode-regression') assert.equal(r.passed, true);
    else assert.equal(e.kind, 'native-runtime');
    return {...e, passed: r.passed, functional_smoke_passed: r.functional_smoke_passed,
      clean_machine: r.clean_machine, os_firewall_isolation: r.os_firewall_isolation,
      findings: r.native_isolation_findings || []};
  });
  const provenance = JSON.parse(s.pinned(s.safe(root, 'models/provenance.json'), cfg.provenance_sha256));
  assert.deepEqual(cfg.models, {translation: provenance.translation, sentence_boundary: provenance.sentence_boundary});
  const sourcePaths = git(root, ['ls-tree', '-r', '--name-only', cfg.source_commit]).toString().trim().split('\n')
    .filter(f => /^(src|scripts|packaging|tests)\//.test(f) ||
      /^(LICENSE|README\.md|pyproject\.toml|requirements(?:-dev)?\.lock|models\/provenance\.json)$/.test(f) ||
      /^docs\/(development|protocol-v1|model-provisioning)\.md$/.test(f));
  assert(sourcePaths.includes('packaging/worker.spec') && sourcePaths.some(p => p.startsWith('src/')));
  const repository = s.zipMembers(git(root, ['archive', '--format=zip', cfg.source_commit, '--', ...sourcePaths]));
  const usage = fs.readFileSync(s.safe(root, 'README.md'));
  const verifier = fs.readFileSync(s.safe(root, 'scripts/verify_release_checksums.ps1'));
  const schema = fs.readFileSync(s.safe(root, 'packaging/release-manifest.schema.json'));
  const workerEntries = new Map();
  for (const [file, sha] of Object.entries(candidate.audit.all_file_sha256)) {
    assert(!excludedVC.test(path.posix.basename(file)), 'Excluded VC DLL reintroduced');
    workerEntries.set('translation-engine-worker/' + file, s.pinned(s.safe(candidate.worker, file), sha));
  }
  for (const file of compliance.files.filter(f => f.path.startsWith('licenses/') || f.path.startsWith('docs/') ||
    ['LICENSE', 'SOURCE_AVAILABILITY.md', 'THIRD_PARTY_NOTICES.md', 'THIRD_PARTY_NOTICES.txt', 'BLOCKERS.txt'].includes(f.path))) {
    workerEntries.set('translation-engine-worker/release-info/' + file.path, s.pinned(s.safe(complianceDir, file.path), file.sha256));
  }
  workerEntries.set('translation-engine-worker/release-info/WINDOWS-CANDIDATE.md', usage);
  for (const file of ['README.md', 'docs/development.md', 'docs/protocol-v1.md',
    'docs/releasing.md', 'docs/troubleshooting.md'])
    workerEntries.set('translation-engine-worker/release-info/' + file, fs.readFileSync(s.safe(root, file)));
  const allCompliance = new Map(s.walk(complianceDir).map(f => [f, fs.readFileSync(s.safe(complianceDir, f))]));
  const sources = new Map([...allCompliance].filter(([f]) => f.startsWith('sources/') || f.startsWith('licenses/') ||
    ['SOURCE_AVAILABILITY.md', 'LICENSE', 'THIRD_PARTY_NOTICES.md', 'evidence/build.json'].includes(f)));
  for (const [file, content] of repository) if (!file.endsWith('/')) sources.set('repository/' + file, content());
  for (const file of ['scripts/assemble_release.cjs', 'scripts/stage_compliance.cjs', 'scripts/verify_release_checksums.ps1',
    'packaging/release-candidate.json', 'packaging/release-manifest.schema.json', 'README.md',
    'docs/development.md', 'docs/protocol-v1.md', 'docs/releasing.md', 'docs/troubleshooting.md'])
    sources.set('assembly/' + file, fs.readFileSync(s.safe(root, file)));
  sources.set('SOURCE_COMMIT.json', Buffer.from(s.json({repository: REPO, commit: cfg.source_commit,
    materials_commit: cfg.materials_commit, source_url: REPO + '/tree/' + cfg.source_commit,
    release_tag: null, tag_rule: 'Future immutable tag must resolve to a commit with these unchanged binary build inputs; otherwise build and revalidate a new candidate.'})));
  const payload = new Map([[WORKER, zip(workerEntries)], [COMPLIANCE, zip(allCompliance)], [SOURCE, zip(sources)],
    ['WINDOWS-CANDIDATE.md', usage], ['verify-checksums.ps1', verifier], ['manifest.schema.json', schema]]);
  const roles = ['worker', 'compliance', 'corresponding-source-preparation', 'usage', 'checksum-verifier', 'manifest-schema'];
  const manifest = validateManifest({schema_version: 1, candidate_id: cfg.candidate_id, worker_version: cfg.worker_version,
    protocol_version: 1, platform: 'windows', architecture: 'x64',
    source: {repository: REPO, commit: cfg.source_commit, materials_commit: cfg.materials_commit, url: REPO + '/tree/' + cfg.source_commit},
    publication: {status: 'local-candidate', tag: null, release_url: null, release_ready: false},
    baseline: {worker: inv.candidate.worker, executable_sha256: inv.candidate.exe_sha256,
      diagnostic_zip_sha256: inv.candidate.zip_sha256, audit_sha256: inv.candidate.audit.sha256,
      build_sha256: inv.candidate.build.sha256, native_files: candidate.audit.pe_count},
    backend: 'argos', dependencies: inv.components.filter(c => c.pyz_roots?.length || ['python', 'pyinstaller'].includes(c.id))
      .map(c => ({id: c.id, version: c.version, source_identity: c.source_identity})),
    external_prerequisites: inv.candidate.external_prerequisites,
    external_models: Object.entries(cfg.models).map(([role, model]) => ({role, ...model, bundled: false})),
    artifacts: [...payload].map(([name, b], index) => ({name, bytes: b.length, sha256: s.hash(b), role: roles[index]})),
    worker_files: [...workerEntries].map(([name, b]) => ({name, bytes: b.length, sha256: s.hash(b)})).sort((a, b) => a.name < b.name ? -1 : 1),
    evidence, compliance: {ready: false, archive: COMPLIANCE, source_archive: SOURCE,
      staged_manifest_sha256: cfg.compliance_manifest_sha256, blockers: compliance.blockers},
    blockers: ['Intel/native redistribution and NumPy renamed Microsoft DLL terms remain unresolved.',
      'Remaining corresponding-source/license supplier mappings and final immutable public delivery remain pending.',
      'Full Windows 10 22H2 x64 acceptance remains pending; Windows 11 is expected compatible, UNTESTED, and optional for v0.1.0.',
      'OS-denied networking and complete clean-target measurements remain pending.', 'Final explicit publication approval has not been given.'],
    assembly: {node: process.versions.node, zlib: process.versions.zlib,
      config_sha256: s.hash(fs.readFileSync(configPath)), tool_sha256: s.hash(fs.readFileSync(__filename))}});
  payload.set('manifest.json', Buffer.from(s.json(manifest)));
  payload.set('SHA256SUMS', Buffer.from([...payload].sort(([a], [b]) => a < b ? -1 : 1)
    .map(([f, b]) => s.hash(b) + '  ' + f + '\n').join('')));
  return {payload, manifest, audit: candidate.audit, workerEntries, sources, allCompliance};
}
function validateWorker(bytes, manifest, audit) {
  // The worker alone is >128 MiB expanded. The compliance reader is intentionally
  // tighter; its caller supplies a reviewed bound for this specific onedir.
  const entries = s.zipMembers(bytes, false, 256 * 1024**2);
  assert.deepEqual([...entries.keys()].sort(), manifest.worker_files.map(f => f.name).sort(), 'Worker archive file coverage differs');
  for (const f of manifest.worker_files) {
    const b = entries.get(f.name)(); assert.equal(b.length, f.bytes); assert.equal(s.hash(b), f.sha256);
    assert(!forbidden(f.name)); assert(!excludedVC.test(path.posix.basename(f.name)));
  }
  for (const [file, sha] of Object.entries(audit.all_file_sha256))
    assert.equal(s.hash(entries.get('translation-engine-worker/' + file)()), sha, 'Original worker bytes changed');
  assert([...entries.keys()].some(f => /numpy\.libs\/msvcp140-.*\.dll$/.test(f)), 'NumPy runtime missing');
}
function verifyFiles(output, payload) {
  assert.deepEqual(s.walk(output), [...payload.keys()].sort(), 'Candidate file coverage differs');
  for (const [file, bytes] of payload) assert(fs.readFileSync(s.safe(output, file)).equals(bytes), 'Candidate differs: ' + file);
}
function assemble(root, configPath, output, check = false) {
  output = outputPath(root, output);
  // rc.1 is immutable. Verify its complete pinned payload rather than regenerating
  // its historical instructions with today's documentation and assembly tool.
  if (check) {
    const manifestBytes = fs.readFileSync(s.safe(output, 'manifest.json'));
    if (s.hash(manifestBytes) === 'c3451790abf20551e470048a417d0653a6802a055ee3d382151c26029d02cb5f') {
      const m = validateManifest(JSON.parse(manifestBytes));
      s.pinned(configPath, m.assembly.config_sha256);
      const cfg = JSON.parse(fs.readFileSync(configPath));
      assert.equal(cfg.source_commit, m.source.commit);
      assert.equal(cfg.materials_commit, m.source.materials_commit);
      assert.equal(cfg.compliance_manifest_sha256, m.compliance.staged_manifest_sha256);
      const invPath = s.safe(root, 'packaging/compliance-inventory.json');
      const inv = JSON.parse(fs.readFileSync(invPath));
      const candidate = s.verifyCandidate(root, inv);
      const inputs = Object.keys(candidate.build.source_sha256).filter(f => f !== 'packaging/compliance-inventory.json');
      for (const commit of [cfg.source_commit, cfg.materials_commit])
        assert.equal(git(root, ['rev-parse', commit]).toString().trim(), commit);
      git(root, ['diff', '--exit-code', cfg.source_commit, '--', ...inputs]);
      git(root, ['diff', '--exit-code', cfg.source_commit, cfg.materials_commit, '--', ...inputs]);
      for (const e of cfg.regression_evidence) s.pinned(s.safe(root, e.path), e.sha256);
      s.pinned(s.safe(root, 'models/provenance.json'), cfg.provenance_sha256);
      s.verifyStage(root, invPath, s.safe(root, cfg.compliance_directory));
      s.pinned(s.safe(root, cfg.compliance_directory + '/manifest.json'), cfg.compliance_manifest_sha256);
      const payload = new Map(m.artifacts.map(a => {
        const bytes = s.pinned(s.safe(output, a.name), a.sha256);
        assert.equal(bytes.length, a.bytes);
        return [a.name, bytes];
      }));
      payload.set('manifest.json', manifestBytes);
      payload.set('SHA256SUMS', Buffer.from([...payload].sort(([a], [b]) => a < b ? -1 : 1)
        .map(([f, b]) => s.hash(b) + '  ' + f + '\n').join('')));
      verifyFiles(output, payload);
      validateWorker(payload.get(WORKER), m, candidate.audit);
      return m;
    }
  }
  const p = prepare(root, configPath);
  validateWorker(p.payload.get(WORKER), p.manifest, p.audit);
  if (!check) {
    assert(!fs.existsSync(output), 'Output already exists'); fs.mkdirSync(output, {recursive: true});
    for (const [file, bytes] of p.payload) fs.writeFileSync(s.safe(output, file), bytes, {flag: 'wx'});
  }
  verifyFiles(output, p.payload);
  const actual = validateManifest(JSON.parse(fs.readFileSync(s.safe(output, 'manifest.json'), 'utf8')));
  assert.equal(actual.source.commit, p.manifest.source.commit, 'Source commit differs');
  return p.manifest;
}
if (require.main === module) {
  try {
    const args = process.argv.slice(2), check = args[0] === '--check'; if (check) args.shift();
    assert.equal(args.length, 1, 'Usage: node scripts/assemble_release.cjs [--check] candidate-staging/NEW-NAME');
    const m = assemble(ROOT, s.safe(ROOT, 'packaging/release-candidate.json'), args[0], check);
    console.log(s.json({candidate: m.candidate_id, source_commit: m.source.commit, release_ready: false, artifacts: m.artifacts}));
  } catch (error) { console.error(error.message); process.exitCode = 1; }
}
module.exports = {zip, crc32, forbidden, validateManifest, validateWorker, verifyFiles, prepare, assemble};
