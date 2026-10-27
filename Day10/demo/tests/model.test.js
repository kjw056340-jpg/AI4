import test from 'node:test';
import assert from 'node:assert/strict';
import { createInitialState, mask, initialKeywords, paginate, validateRegistration, requireOwner } from '../public/model.js';

test('pagination defaults to 10, preserves remainder and clamps invalid pages', () => {
  const posts = createInitialState().posts;
  assert.equal(paginate(posts, 1).items.length, 10);
  assert.equal(paginate(posts, 2).items.length, 10);
  assert.equal(paginate(posts, 3).items.length, 3);
  assert.equal(paginate(posts, 100).current, 3);
  assert.equal(paginate([], 1).pages, 1);
});
test('masks literal, spaced, numbered, compatibility and English variants', () => {
  assert.equal(mask('씨발 / 씨 1발 / ㅅㅂ / FUCK', initialKeywords), '** / **** / ** / ****');
  assert.equal(mask('평범한 기록과 shift', initialKeywords), '평범한 기록과 shift');
  assert.equal(mask('f.u.c.k', initialKeywords), '*******');
  assert.equal(mask('a+b aab', ['a+b']), '*** aab');
});
test('keyword changes apply retroactively without destroying original', () => {
  const original = '오늘은 특별한 날';
  assert.equal(mask(original, ['특별']), '오늘은 **한 날');
  assert.equal(mask(original, []), original);
});
test('registration rejects duplicate email case, invalid email, blank name and short passwords', () => {
  const { users } = createInitialState();
  assert.throws(() => validateRegistration(users, 'DEMO@note.demo', '새회원', 'valid123'));
  assert.throws(() => validateRegistration(users, 'wrong', '새회원', 'valid123'));
  assert.throws(() => validateRegistration(users, 'new@note.demo', '  ', 'valid123'));
  assert.throws(() => validateRegistration(users, 'new@note.demo', '새회원', '123'));
  assert.doesNotThrow(() => validateRegistration(users, 'new@note.demo', '새회원', 'valid123'));
});
test('ownership allows only the author, including excluding admin', () => {
  const { posts, users } = createInitialState();
  assert.doesNotThrow(() => requireOwner(posts[0], users[0]));
  assert.throws(() => requireOwner(posts[0], users[1]));
  assert.throws(() => requireOwner(posts[0], users.at(-1)));
  assert.throws(() => requireOwner(posts[0], null));
});
