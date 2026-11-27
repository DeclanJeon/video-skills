// Static reference regression only: not agent compliance or final-video QA.
import assert from 'node:assert/strict';
import { readFileSync, realpathSync, existsSync, readdirSync } from 'node:fs';
import { dirname, resolve, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { homedir } from 'node:os';
import test from 'node:test';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const read = (path) => readFileSync(join(root, path), 'utf8');
const entry = read('SKILL.md');
const slot = read('references/postproduction-slot.md');

test('public entry advertises post-only requests', () => {
  assert.match(entry, /description:.*postproduction/);
  assert.match(entry, /\| 포스트프로덕션만[^\n]*video-postproduction-skills\/SKILL.md/);
});

test('final route links actual post entry and retains explicit endpoints', () => {
  const finalRow = entry.split('\n').find(line => line.startsWith('| 최종 영상까지/논스톱'));
  assert.ok(finalRow?.includes('video-postproduction-skills/SKILL.md'));
  assert.match(entry, /명시 종료점/);
  assert.match(entry, /G0/);
});

test('post connection references actual intake, execution and delivery contracts', () => {
  for (const term of [
    'video-postproduction-skills/SKILL.md', 'references/execution-contract.md',
    'IntakeRequest', 'intake', 'validate', 'inspect-env', 'prepare', 'observe',
    'review', 'deliver', 'PG-E', 'PG0–PG6', 'receiver', 'production-ledger.json',
  ]) assert.ok(slot.includes(term), term);
});

test('active routing no longer declares existing post entry unavailable', () => {
  for (const path of ['SKILL.md', 'references/phase-contract.md', 'references/postproduction-slot.md']) {
    assert.doesNotMatch(read(path), /entry unavailable|SKILL.md가 없어|진입 파일이 없/);
  }
});

test('every local markdown reference in active entry and connection resolves', () => {
  for (const path of ['SKILL.md', 'references/phase-contract.md', 'references/postproduction-slot.md']) {
    for (const match of read(path).matchAll(/\]\(([^)]+)\)/g)) {
      const target = match[1].split('#')[0];
      if (!target || /^[a-z]+:\/\//i.test(target)) continue;
      assert.ok(existsSync(resolve(root, dirname(path), target)), path + ': ' + target);
    }
  }
});

test('phase entries keep disabled automatic invocation and completion safety', () => {
  for (const path of [
    'video-preproduction-skills/production-director/SKILL.md',
    'video-production-skills/production-supervisor/SKILL.md',
    'video-postproduction-skills/SKILL.md',
  ]) assert.match(read(path), /disable-model-invocation: true/);
  for (const term of ['sources_ready', 'handed_off', 'master_delivered', '승인', '권리']) {
    assert.ok(entry.includes(term), term);
  }
  assert.match(slot, /technical_fixture/);
  assert.match(slot, /명시 동의/);
});

const localRoots = ['.agents/skills', '.codex/skills', '.claude/skills',
  '.pi/agent/skills', '.gemini/skills', '.config/opencode/skills'];
const installed = localRoots.every(path => existsSync(join(homedir(), path, 'video-skills')));
test('installed registrations expose canonical skill bytes, not stale copies', {
  skip: installed ? false : 'local six-agent installation not present',
}, () => {
  const skills = [];
  const walk = (dir) => {
    for (const item of readdirSync(dir, { withFileTypes: true })) {
      if (item.name.startsWith('.')) continue;
      const path = join(dir, item.name);
      if (item.isDirectory()) walk(path);
      else if (item.name === 'SKILL.md') skills.push(path);
    }
  };
  walk(root);
  for (const base of localRoots) {
    const registered = join(homedir(), base, 'video-skills');
    assert.equal(realpathSync(registered), realpathSync(root));
    for (const phase of ['video-preproduction-skills', 'video-production-skills', 'video-postproduction-skills']) {
      assert.equal(realpathSync(join(homedir(), base, phase)), realpathSync(join(root, phase)));
    }
    for (const source of skills) {
      assert.deepEqual(readFileSync(join(registered, source.slice(root.length + 1))), readFileSync(source));
    }
  }
});

test('shared workflow defers phase availability to canonical contracts', {
  skip: existsSync(join(homedir(), '.agents/DEVELOPMENT-WORKFLOWS.md')) ? false : 'local workflow not present',
}, () => {
  const shared = readFileSync(join(homedir(), '.agents/DEVELOPMENT-WORKFLOWS.md'), 'utf8');
  const content = shared.split('## Content production')[1];
  assert.ok(content);
  assert.doesNotMatch(content, /no SKILL.md entry|execution remains blocked|entry unavailable/);
  assert.ok(content.includes('references/phase-contract.md'));
  assert.ok(content.includes('video-postproduction-skills/SKILL.md'));
});
