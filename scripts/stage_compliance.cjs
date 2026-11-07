/* Offline candidate-specific compliance staging. Node >=22; no npm packages. */
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const zlib = require('node:zlib');
const ROOT = path.resolve(__dirname, '..');
const hash = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const json = value => JSON.stringify(value, null, 2) + '\n';
const read = file => JSON.parse(fs.readFileSync(file, 'utf8'));
const assert = (ok, message) => { if (!ok) throw new Error(message); };
const model = name => /\.(onnx|argosmodel)$/i.test(name);

function safe(base, relative) {
  assert(typeof relative === 'string' && relative.length && !relative.includes('\\') &&
    !relative.includes(':') && !relative.split('/').some(p => ['', '.', '..'].includes(p)) &&
    !path.isAbsolute(relative), 'Unsafe relative path: ' + relative);
  const resolved = path.resolve(base, relative);
  assert(resolved.startsWith(path.resolve(base) + path.sep), 'Path escapes root');
  // Do not follow junctions/symlinks in either inputs or output directories.
  let current = path.resolve(base);
  for (const part of ['', ...relative.split('/')]) {
    current = path.join(current, part);
    if (fs.existsSync(current)) assert(!fs.lstatSync(current).isSymbolicLink(), 'Link refused: ' + current);
  }
  return resolved;
}

function walk(base, prefix = '') {
  return fs.readdirSync(safeDirectory(base, prefix), {withFileTypes: true})
    .sort((a, b) => a.name < b.name ? -1 : a.name > b.name ? 1 : 0).flatMap(e => {
      const name = prefix ? prefix + '/' + e.name : e.name;
      assert(!e.isSymbolicLink(), 'Link refused: ' + name);
      if (e.isDirectory()) return walk(base, name);
      assert(e.isFile(), 'Non-regular file: ' + name);
      return [name];
    }).sort();
}
function safeDirectory(base, prefix) { return prefix ? safe(base, prefix) : base; }
function pinned(file, expected) {
  assert(/^[a-f0-9]{64}$/.test(expected || ''), 'Missing SHA-256: ' + file);
  const bytes = fs.readFileSync(file);
  assert(hash(bytes) === expected, 'SHA-256 mismatch: ' + file);
  return bytes;
}

// Read-only bounded ZIP reader: only stored/deflated, nonencrypted, non-ZIP64.
// Members are never extracted by archive-controlled filesystem paths.
function zipMembers(bytes, allowUnselectedModels = false) {
  let end = -1;
  for (let p = bytes.length - 22; p >= Math.max(0, bytes.length - 65557); p--) {
    if (bytes.readUInt32LE(p) === 0x06054b50 && p + 22 + bytes.readUInt16LE(p + 20) === bytes.length) { end = p; break; }
  }
  assert(end >= 0, 'Invalid ZIP end');
  const count = bytes.readUInt16LE(end + 10), size = bytes.readUInt32LE(end + 12);
  let pos = bytes.readUInt32LE(end + 16), total = 0;
  assert(bytes.readUInt32LE(end + 4) === 0 && count === bytes.readUInt16LE(end + 8) &&
    count < 10000 && pos + size === end, 'Unsupported ZIP layout');
  const members = new Map();
  for (let i = 0; i < count; i++) {
    assert(pos + 46 <= end && bytes.readUInt32LE(pos) === 0x02014b50, 'Invalid ZIP directory');
    const flags = bytes.readUInt16LE(pos + 8), method = bytes.readUInt16LE(pos + 10);
    const packed = bytes.readUInt32LE(pos + 20), length = bytes.readUInt32LE(pos + 24);
    const nameLength = bytes.readUInt16LE(pos + 28), extra = bytes.readUInt16LE(pos + 30), comment = bytes.readUInt16LE(pos + 32);
    const local = bytes.readUInt32LE(pos + 42);
    const name = bytes.subarray(pos + 46, pos + 46 + nameLength).toString('utf8');
    assert(!(flags & 1) && [0, 8].includes(method) && packed !== 0xffffffff && length <= 64 * 1024**2, 'Unsupported ZIP entry: ' + name);
    const isLink = ((bytes.readUInt32LE(pos + 38) >>> 16) & 0xf000) === 0xa000;
    safe(ROOT, name.replace(/\/$/, ''));
    assert(allowUnselectedModels || !model(name), 'External model in archive: ' + name);
    assert(!members.has(name), 'Duplicate ZIP member: ' + name);
    total += length;
    assert(total <= 128 * 1024**2, 'ZIP exceeds expanded size bound');
    assert(local + 30 <= bytes.length && bytes.readUInt32LE(local) === 0x04034b50, 'Invalid ZIP local header');
    const start = local + 30 + bytes.readUInt16LE(local + 26) + bytes.readUInt16LE(local + 28);
    assert(start + packed <= bytes.readUInt32LE(end + 16), 'ZIP member out of bounds');
    const localName = bytes.subarray(local + 30, local + 30 + bytes.readUInt16LE(local + 26)).toString('utf8');
    assert(localName === name && bytes.readUInt16LE(local + 8) === method, 'ZIP header mismatch');
    const content = () => {
      const raw = bytes.subarray(start, start + packed);
      const output = method === 0 ? raw : zlib.inflateRawSync(raw, {maxOutputLength: 64 * 1024**2});
      assert(output.length === length, 'ZIP length mismatch: ' + name);
      return output;
    };
    // Preserve upstream source ZIP links as archive bytes, never filesystem links.
    if (isLink) {
      const target = content().toString('utf8');
      assert(!path.posix.isAbsolute(target) && !/[\\:\r\n\0]/.test(target), 'Unsafe ZIP link');
      safe(ROOT, path.posix.normalize(path.posix.join(path.posix.dirname(name), target)));
    }
    members.set(name, content);
    pos += 46 + nameLength + extra + comment;
  }
  assert(pos === end, 'ZIP directory size mismatch');
  return members;
}

function pyzRoots(text) {
  return [...new Set([...text.matchAll(/^\s*\[?\('([^']+)',/gm)].map(m => m[1])
    .filter(n => !/[\\/:]/.test(n)).map(n => n.split('.')[0]))].sort();
}

function validateInventory(inv) {
  assert(inv.schema_version === 1 && inv.scope === 'preparatory-only', 'Unsupported inventory');
  assert(Array.isArray(inv.components) && inv.components.length > 0 && inv.obligations.length > 0, 'Empty inventory/gates');
  const ids = new Set(), owners = new Map();
  for (const c of inv.components) {
    assert(c.id && !ids.has(c.id), 'Duplicate/missing component'); ids.add(c.id);
    assert(c.name && c.version && c.redistributed_form && c.license &&
      ['verified', 'incomplete', 'blocked'].includes(c.status) &&
      ['yes', 'conditional', 'no'].includes(c.matching_source_required) && Array.isArray(c.materials) &&
      Array.isArray(c.blockers), 'Incomplete component: ' + c.id);
    assert(c.status === 'verified' || c.blockers.length, 'Missing blocker: ' + c.id);
    for (const f of c.worker_files) { assert(!owners.has(f), 'Duplicate file owner: ' + f); owners.set(f, c.id); }
    for (const m of c.materials) {
      safe(ROOT, m.destination);
      assert(!model(m.destination) && m.required === true && m.kind && m.source, 'Invalid material: ' + c.id);
    }
    assert(c.materials.length || c.blockers.length, 'No materials/evidence: ' + c.id);
  }
  for (const o of inv.obligations) assert(o.id && o.blocker && o.status === 'blocked', 'Unreviewed obligation');
  return owners;
}

function verifyCandidate(root, inv) {
  const owners = validateInventory(inv), candidate = inv.candidate;
  const auditBytes = pinned(safe(root, candidate.audit.path), candidate.audit.sha256);
  const audit = JSON.parse(auditBytes);
  assert(audit.passed === true && audit.errors.length === 0, 'Worker audit failed');
  assert(audit.exe_sha256 === candidate.exe_sha256 && audit.zip_sha256 === candidate.zip_sha256, 'Candidate identity mismatch');
  const worker = safe(root, candidate.worker);
  const files = walk(worker), known = Object.keys(audit.all_file_sha256).sort();
  assert(json(files) === json(known) && known.length === audit.file_count, 'Worker file inventory differs');
  assert(json([...owners.keys()].sort()) === json(known), 'Component inventory does not cover exact worker files');
  for (const f of known) { assert(!model(f), 'External model in worker'); pinned(safe(worker, f), audit.all_file_sha256[f]); }
  const toc = pinned(safe(root, candidate.pyz.path), candidate.pyz.sha256).toString('utf8');
  assert(json(pyzRoots(toc)) === json(candidate.pyz_roots), 'Frozen PYZ roots differ');
  const mapped = inv.components.flatMap(c => c.pyz_roots || []).sort();
  assert(json(mapped) === json(candidate.third_party_roots), 'Missing/duplicate frozen distribution');
  assert(candidate.third_party_roots.every(r => candidate.pyz_roots.includes(r)), 'Unfrozen component root');
  const build = JSON.parse(pinned(safe(root, candidate.build.path), candidate.build.sha256));
  assert(build.passed === true, 'Build evidence failed');
  for (const [file, sha] of Object.entries(build.source_sha256)) pinned(safe(root, file), sha);
  const locks = ['requirements.lock', 'requirements-dev.lock'].filter(f => fs.existsSync(safe(root, f)))
    .map(f => fs.readFileSync(safe(root, f), 'utf8')).join('\n');
  for (const c of inv.components) {
    if (c.source_identity.wheel_sha256) assert(locks.includes('sha256:' + c.source_identity.wheel_sha256), 'Wheel not in candidate locks: ' + c.id);
  }
  return {audit, build, worker};
}

function sourceBytes(root, source, archives) {
  if (source.member) {
    assert(!model(source.member), 'External model member refused');
    const key = source.path + ':' + source.archive_sha256;
    if (!archives.has(key)) archives.set(key, zipMembers(pinned(safe(root, source.path), source.archive_sha256), true));
    const member = archives.get(key).get(source.member);
    assert(member, 'Missing archive member: ' + source.member);
    const bytes = member(); assert(hash(bytes) === source.sha256, 'Archive material hash mismatch');
    return bytes;
  }
  if (source.external_path) {
    // Only the exact observed Python supplier license is an external input.
    assert(source.role === 'python-distribution-license' && path.isAbsolute(source.external_path) &&
      path.basename(source.external_path) === 'LICENSE.txt', 'Unapproved external source');
    return pinned(source.external_path, source.sha256);
  }
  const file = safe(root, source.path);
  assert(!model(file), 'External model material refused');
  const bytes = pinned(file, source.sha256);
  if (/\.(zip|whl)$/i.test(file)) zipMembers(bytes); // Reject hidden model members too.
  return bytes;
}

function stagingBase(root, output) {
  const base = safe(root, 'candidate-staging');
  const destination = path.resolve(output);
  assert(destination.startsWith(base + path.sep), 'Output must be below candidate-staging/');
  safe(root, path.relative(root, destination).split(path.sep).join('/'));
  return destination;
}

function blockerText(blockers) {
  return 'PREPARATORY COMPLIANCE STAGING - NOT RELEASE READY\n\n' +
    blockers.map(b => b.component + ' [' + b.id + ']: ' + b.reason + '\n').join('');
}

function noticeIndex(inv, files) {
  return 'THIRD-PARTY MATERIALS INDEX - PREPARATORY, NOT A LICENSE CLEARANCE\n' +
    'Candidate EXE SHA-256: ' + inv.candidate.exe_sha256 + '\n' +
    'Original third-party texts are copied byte-for-byte at the paths below.\n' +
    'License identity does not grant rights to other bundled components.\n' +
    'See BLOCKERS.txt and manifest.json for unfulfilled obligations.\n\n' +
    inv.components.map(c => c.name + ' | ' + c.version + '\n' +
      'License: ' + c.license + '\nInventory status: ' + c.status + '\n' +
      files.filter(f => f.component === c.id && /license|notice/.test(f.kind))
        .sort((a, b) => a.path < b.path ? -1 : 1)
        .map(f => '  ' + f.path + '\n').join('') +
      (c.evidence_materials_from ? 'Shared supplier materials: ' + c.evidence_materials_from.join(', ') + '\n' : '') + '\n').join('');
}

function stage(root, inventoryPath, output) {
  const inventoryBytes = fs.readFileSync(inventoryPath), inv = JSON.parse(inventoryBytes);
  const candidate = verifyCandidate(root, inv);
  output = stagingBase(root, output);
  assert(!fs.existsSync(output), 'Output already exists; use a new staging directory');
  const blockers = inv.obligations.map(o => ({component: 'distribution', id: o.id, reason: o.blocker}));
  const payload = new Map(), archives = new Map(), results = [];
  function add(name, bytes, component, kind, origin) {
    safe(output, name); assert(!model(name) && !payload.has(name), 'Duplicate/forbidden staged file: ' + name);
    payload.set(name, {bytes, component, kind, origin});
  }
  add('evidence/component-inventory.json', inventoryBytes, 'distribution', 'inventory', 'reviewed input');
  add('evidence/stage_compliance.cjs', fs.readFileSync(__filename), 'distribution', 'staging-tool', 'scripts/stage_compliance.cjs');
  for (const [name, item] of Object.entries(inv.candidate)) {
    if (item && item.path && item.sha256) add('evidence/' + name + path.extname(item.path),
      pinned(safe(root, item.path), item.sha256), 'distribution', 'candidate-evidence', item.path);
  }
  for (const c of inv.components) {
    for (const reason of c.blockers) blockers.push({component: c.id, id: 'review', reason});
    let count = 0;
    for (const m of c.materials) {
      try { add(m.destination, sourceBytes(root, m.source, archives), c.id, m.kind, m.source); count++; }
      catch (e) { blockers.push({component: c.id, id: 'material:' + m.destination, reason: e.message}); }
    }
    results.push({id: c.id, name: c.name, version: c.version, license: c.license,
      status: c.status === 'verified' && count === c.materials.length ? 'verified' : c.status === 'blocked' ? 'blocked' : 'incomplete',
      staged_materials: count, matching_source_required: c.matching_source_required,
      source_identity: c.source_identity, source_complete: false});
  }
  // Exact worker/build inputs, not a current checkout archive with unrelated files.
  for (const [file, sha] of Object.entries(candidate.build.source_sha256))
    add('sources/worker/' + file, pinned(safe(root, file), sha), 'translation-engine', 'build-input', file);
  blockers.sort((a, b) => json(a) < json(b) ? -1 : json(a) > json(b) ? 1 : 0);
  add('BLOCKERS.txt', Buffer.from(blockerText(blockers)), 'distribution', 'blocker-report', 'derived from inventory and material checks');
  add('THIRD_PARTY_NOTICES.txt', Buffer.from(noticeIndex(inv, [...payload].map(([name, p]) =>
    ({path: name, component: p.component, kind: p.kind})))), 'distribution', 'notice-index', 'derived index; original texts remain unmodified');
  const files = [...payload].sort(([a], [b]) => a < b ? -1 : 1).map(([name, p]) =>
    ({path: name, sha256: hash(p.bytes), bytes: p.bytes.length, component: p.component, kind: p.kind, origin: p.origin}));
  const manifest = {schema_version: 1, scope: 'preparatory-only', release_ready: false,
    compliance_ready: false, inventory_sha256: hash(inventoryBytes), candidate: inv.candidate,
    components: results, blockers, files};
  // All reads/validation above precede writes. No worker/build/dist writes or deletion.
  fs.mkdirSync(output, {recursive: true});
  for (const [name, p] of payload) {
    const file = safe(output, name); fs.mkdirSync(path.dirname(file), {recursive: true}); fs.writeFileSync(file, p.bytes, {flag: 'wx'});
  }
  const manifestBytes = Buffer.from(json(manifest)); fs.writeFileSync(path.join(output, 'manifest.json'), manifestBytes, {flag: 'wx'});
  const sums = [...files.map(f => [f.path, f.sha256]), ['manifest.json', hash(manifestBytes)]]
    .sort(([a], [b]) => a < b ? -1 : 1).map(([name, sha]) => sha + '  ' + name + '\n').join('');
  fs.writeFileSync(path.join(output, 'SHA256SUMS'), sums, {flag: 'wx'});
  verifyStage(root, inventoryPath, output);
  return manifest;
}

function verifyStage(root, inventoryPath, output) {
  output = stagingBase(root, output);
  const invBytes = fs.readFileSync(inventoryPath), inv = JSON.parse(invBytes);
  const candidate = verifyCandidate(root, inv);
  const manifest = read(path.join(output, 'manifest.json'));
  assert(manifest.schema_version === 1 && manifest.scope === 'preparatory-only' &&
    manifest.release_ready === false && manifest.compliance_ready === false, 'Preparatory staging cannot declare readiness');
  assert(manifest.inventory_sha256 === hash(invBytes), 'Stale inventory');
  pinned(safe(output, 'evidence/component-inventory.json'), hash(invBytes));
  pinned(safe(output, 'evidence/stage_compliance.cjs'), hash(fs.readFileSync(__filename)));
  assert(json(manifest.candidate) === json(inv.candidate), 'Staged candidate differs');
  assert(manifest.components.length === inv.components.length, 'Component count mismatch');
  for (const c of inv.components) {
    const result = manifest.components.find(r => r.id === c.id && r.version === c.version);
    const failed = manifest.blockers.some(b => b.component === c.id && b.id.startsWith('material:'));
    assert(result && result.status === (failed && c.status === 'verified' ? 'incomplete' : c.status), 'Component status mismatch');
    for (const reason of c.blockers) assert(manifest.blockers.some(b => b.component === c.id && b.reason === reason), 'Missing component blocker');
    for (const m of c.materials) {
      const file = manifest.files.find(f => f.path === m.destination && f.component === c.id);
      assert(file ? file.sha256 === m.source.sha256 && file.kind === m.kind :
        manifest.blockers.some(b => b.component === c.id && b.id === 'material:' + m.destination), 'Unaccounted/mismatched material');
    }
  }
  for (const o of inv.obligations) assert(manifest.blockers.some(b => b.id === o.id && b.reason === o.blocker), 'Missing release blocker');
  assert(fs.readFileSync(safe(output, 'BLOCKERS.txt'), 'utf8') === blockerText(manifest.blockers), 'Blocker report differs');
  assert(fs.readFileSync(safe(output, 'THIRD_PARTY_NOTICES.txt'), 'utf8') === noticeIndex(inv, manifest.files), 'Notice index differs');
  const names = manifest.files.map(f => f.path);
  for (const [file, sha] of Object.entries(candidate.build.source_sha256))
    assert(manifest.files.some(f => f.path === 'sources/worker/' + file && f.sha256 === sha), 'Missing build source: ' + file);
  assert(new Set(names.map(n => n.toLowerCase())).size === names.length, 'Duplicate manifest path');
  assert(json(walk(output)) === json([...names, 'manifest.json', 'SHA256SUMS'].sort()), 'Staging file inventory differs');
  for (const f of manifest.files) {
    assert(!model(f.path), 'External model in staging');
    const bytes = pinned(safe(output, f.path), f.sha256); assert(bytes.length === f.bytes, 'Staged size differs');
    if (/\.(zip|whl)$/i.test(f.path)) zipMembers(bytes);
  }
  const sums = [...manifest.files.map(f => [f.path, f.sha256]), ['manifest.json', hash(fs.readFileSync(path.join(output, 'manifest.json')))]]
    .sort(([a], [b]) => a < b ? -1 : 1).map(([name, sha]) => sha + '  ' + name + '\n').join('');
  assert(fs.readFileSync(path.join(output, 'SHA256SUMS'), 'utf8') === sums, 'SHA256SUMS differs');
  return manifest;
}

if (require.main === module) {
  try {
    const args = process.argv.slice(2), check = args[0] === '--check';
    if (check) args.shift();
    assert(args.length === 1, 'Usage: node scripts\\stage_compliance.cjs [--check] candidate-staging\\NEW-NAME');
    const inventory = path.join(ROOT, 'packaging/compliance-inventory.json');
    const manifest = check ? verifyStage(ROOT, inventory, path.resolve(args[0])) : stage(ROOT, inventory, path.resolve(args[0]));
    console.log(json({scope: manifest.scope, release_ready: false, compliance_ready: false,
      components: manifest.components.length, staged_files: manifest.files.length,
      blockers: manifest.blockers.length, manifest: path.join(args[0], 'manifest.json')}));
    process.exitCode = 2; // Expected blocked-readiness result; never a release approval.
  } catch (e) { console.error(e.message); process.exitCode = 1; }
}
module.exports = {hash, json, safe, walk, pinned, zipMembers, pyzRoots, validateInventory, verifyCandidate, stage, verifyStage};
