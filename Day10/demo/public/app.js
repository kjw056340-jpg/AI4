import { STORAGE_KEY, PAGE_SIZE, createInitialState, mask, paginate, validateRegistration, requireOwner } from './model.js';

let state;
try { state = JSON.parse(localStorage.getItem(STORAGE_KEY)); } catch { /* Start with demo data if storage is corrupt. */ }
if (!state || state.version !== 1 || !Array.isArray(state.posts) || !Array.isArray(state.users) || !Array.isArray(state.keywords)) state = createInitialState();
let view = 'board', page = 1, search = '', selectedId = null, editingId = null;
const app = document.querySelector('#app'), modal = document.querySelector('#modal');
const icons = {
  note: '<rect x="4" y="3" width="16" height="18" rx="3"/><path d="M8 8h8M8 12h8M8 16h5"/>',
  board: '<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>',
  edit: '<path d="m15 5 4 4M4 20l5-1L21 7a2.8 2.8 0 0 0-4-4L5 15z"/>',
  shield: '<path d="M12 3 4 6v6c0 5 8 9 8 9s8-4 8-9V6z"/><path d="m8 12 3 3 5-6"/>',
  search: '<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/>',
  arrow: '<path d="m14 7-5 5 5 5"/>',
  plus: '<path d="M12 5v14M5 12h14"/>',
  chat: '<path d="M21 11.5a8.5 8.5 0 0 1-8.5 8.5H4l-2 2v-9.5A8.5 8.5 0 1 1 21 11.5Z"/>',
  logout: '<path d="M9 4H4v16h5M10 12h12m-4-4 4 4-4 4"/>',
  leaf: '<path d="M20 3C8 2 2 8 6 15s16 5 14-12Z"/><path d="M3 21 15 9"/>',
};
const icon = (name, cls = '') => `<svg class="icon ${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.65" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${icons[name] || icons.note}</svg>`;
const esc = text => String(text ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
const safe = text => esc(mask(text, state.keywords));
const user = () => state.users.find(u => u.id === state.sessionId);
const author = id => state.users.find(u => u.id === id)?.name || '알 수 없는 회원';
const date = value => new Date(value).toLocaleDateString('ko-KR', { month: '2-digit', day: '2-digit' });
const save = () => { localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); };
let toastTimer;
function toast(message) { const el = document.querySelector('#toast'); el.textContent = message; el.classList.add('show'); clearTimeout(toastTimer); toastTimer = setTimeout(() => el.classList.remove('show'), 3200); }
function navigate(next) { view = next; page = 1; search = ''; render(); window.scrollTo(0, 0); }
function persistAndRender(message) { save(); render(); if (message) toast(message); }

function render() {
  const me = user();
  app.innerHTML = `<aside class="sidebar">
    <a class="brand" href="#" data-action="board"><span class="brand-mark">n<span>·</span></span><span>note<span class="brand-light">-demo</span><small>생각이 모이는 곳</small></span></a>
    <div class="nav-label">WORKSPACE</div>
    <nav aria-label="주 메뉴">
      <button class="nav-item ${['board', 'detail', 'write'].includes(view) ? 'active' : ''}" data-action="board">${icon('board')}<span>전체 게시판</span><span class="nav-count">${state.posts.length}</span></button>
      <button class="nav-item ${view === 'mine' ? 'active' : ''}" data-action="mine">${icon('note')}<span>내가 쓴 글</span></button>
      ${me?.role === 'admin' ? `<button class="nav-item ${view === 'admin' ? 'active' : ''}" data-action="admin">${icon('shield')}<span>금칙어 관리</span></button>` : ''}
    </nav>
    <div class="sidebar-bottom"><div class="kind-note">${icon('leaf')}<strong>좋은 대화는<br>작은 배려에서 시작돼요.</strong><p>서로 다른 생각을 존중하고<br>따뜻한 이야기를 나눠주세요.</p></div>
      <div class="sidebar-foot"><span class="status-dot"></span>작은 기록, 더 나은 하루<span>↗</span></div>
    </div>
  </aside>
  <div class="workspace"><header class="topbar"><div class="breadcrumb">커뮤니티 <span>/</span> <strong>${view === 'mine' ? '내가 쓴 글' : view === 'admin' ? '금칙어 관리' : '전체 게시판'}</strong></div><div class="account">${me ? `<span class="avatar">${safe(me.name[0])}</span><span class="account-name">${safe(me.name)} 님</span><button class="icon-button" data-action="logout" aria-label="로그아웃" title="로그아웃">${icon('logout')}</button>` : `<button class="text-button" data-action="login">로그인</button><button class="button small" data-action="signup">회원가입 ${icon('plus')}</button>`}</div></header>
  <main id="main">${view === 'detail' ? detailView() : view === 'write' ? writeView() : view === 'admin' ? adminView() : boardView()}</main>
  <footer><span>© ${new Date().getFullYear()} note-demo</span><span>당신의 생각이 누군가의 영감이 되는 곳.</span><span class="demo-label">LOCAL DEMO</span></footer></div>`;
}
function boardView() {
  const mine = view === 'mine';
  const filtered = state.posts.filter(p => (!mine || p.authorId === user()?.id) && mask(p.title, state.keywords).toLowerCase().includes(search.toLowerCase())).sort((a, b) => b.createdAt.localeCompare(a.createdAt));
  const result = paginate(filtered, page); page = result.current;
  return `<section class="page-heading"><div class="eyebrow">OUR LITTLE COMMUNITY</div><div class="heading-line"><div><h1>${mine ? '내가 쓴 글' : '생각을 남기고, 이야기를 나눠요'}<span class="subtitle">${mine ? '차곡차곡 쌓아온 나의 이야기를 만나보세요.' : '일상의 작은 발견부터 깊은 고민까지. 당신의 이야기를 기다려요.'}</span></div><button class="button" data-action="new">${icon('edit')} 글쓰기</button></div></section>
  <section class="welcome-banner"><div><span class="banner-label">A SPACE FOR YOUR THOUGHTS</span><h2>별일 없는 하루에도,<br>나누고 싶은 이야기는 있으니까.</h2><p>가볍게 적어보세요. 함께 나누면 조금 더 특별해져요.</p></div><div class="paper-art" aria-hidden="true"><div class="art-circle"></div><div class="paper paper-back"></div><div class="paper paper-front"><span class="paper-tape"></span><span class="paper-word">dear, today</span><i></i><i></i><i></i><span class="paper-leaf">${icon('leaf')}</span></div><span class="art-spark">✧</span><span class="art-dot"></span></div></section>
  <section class="board-section" aria-label="게시글 목록"><div class="board-toolbar"><div class="board-tab">${mine ? '내 게시글' : '전체 글'} <span>${filtered.length}</span></div><form id="search-form" class="search-box">${icon('search')}<input name="search" aria-label="제목 검색" placeholder="제목으로 검색해 보세요" value="${esc(search)}" maxlength="100"><button class="text-button" type="submit">검색</button></form></div>
  <div class="table-wrap"><table><thead><tr><th class="number">번호</th><th class="title-column">제목</th><th class="author-column">작성자</th><th class="date-column">작성일</th></tr></thead><tbody>${result.items.map((p, i) => `<tr><td class="number">${filtered.length - ((page - 1) * PAGE_SIZE + i)}</td><td><button class="post-title" data-action="detail" data-id="${esc(p.id)}">${safe(p.title)}${p.comments.length ? `<span class="comment-count">${p.comments.length}</span>` : ''}${Date.now() - new Date(p.createdAt).getTime() < 86400000 ? '<span class="new-label">N</span>' : ''}</button></td><td class="author-column"><span class="mini-avatar color-${state.users.findIndex(u => u.id === p.authorId) % 4}">${safe(author(p.authorId)[0])}</span>${safe(author(p.authorId))}</td><td class="date-column">${date(p.createdAt)}</td></tr>`).join('') || `<tr><td colspan="4" class="empty">${search ? '검색 결과가 없어요. 다른 제목으로 찾아보세요.' : '아직 글이 없어요. 첫 이야기를 남겨보세요.'}</td></tr>`}</tbody></table></div>
  <div class="table-bottom"><span>페이지당 ${PAGE_SIZE}개 표시</span><nav class="pagination" aria-label="페이지 이동"><button class="page-button" data-action="page" data-page="${page - 1}" ${page === 1 ? 'disabled' : ''} aria-label="이전 페이지">${icon('arrow')}</button>${Array.from({ length: result.pages }, (_, i) => `<button class="page-button ${page === i + 1 ? 'current' : ''}" data-action="page" data-page="${i + 1}" ${page === i + 1 ? 'aria-current="page"' : ''}>${i + 1}</button>`).join('')}<button class="page-button next" data-action="page" data-page="${page + 1}" ${page === result.pages ? 'disabled' : ''} aria-label="다음 페이지">${icon('arrow')}</button></nav><span>총 ${filtered.length}개의 이야기</span></div></section>
  <div class="safety-note">${icon('shield')}<span>서로를 위한 안전한 공간 <b>·</b> 불쾌한 표현은 자동으로 마스킹됩니다.</span><span class="safety-tag">클린 커뮤니티</span></div>`;
}
function detailView() {
  const p = state.posts.find(p => p.id === selectedId);
  if (!p) { view = 'board'; return boardView(); }
  const own = p.authorId === user()?.id;
  return `<button class="back-link" data-action="board">${icon('arrow')} 목록으로</button><article class="article"><div class="eyebrow">COMMUNITY NOTE</div><h1>${safe(p.title)}</h1><div class="article-meta"><span class="mini-avatar">${safe(author(p.authorId)[0])}</span>${safe(author(p.authorId))}<span>·</span>${new Date(p.createdAt).toLocaleString('ko-KR')}${p.updatedAt ? '<span>· 수정됨</span>' : ''}</div><div class="article-content">${safe(p.content)}</div>${own ? `<div class="article-actions"><button class="button secondary" data-action="edit" data-id="${p.id}">수정</button><button class="button danger" data-action="delete" data-id="${p.id}">삭제</button></div>` : ''}</article>
  <section class="comments"><h2>댓글 <span>${p.comments.length}</span></h2>${p.comments.map(c => `<div class="comment"><span class="avatar">${safe(author(c.authorId)[0])}</span><div><strong>${safe(author(c.authorId))}</strong><small>${new Date(c.createdAt).toLocaleString('ko-KR')}</small><p>${safe(c.content)}</p></div></div>`).join('') || '<p class="muted">첫 번째 댓글로 이야기를 이어가 보세요.</p>'}${user() ? `<form id="comment-form"><label class="sr-only" for="comment-content">댓글 내용</label><textarea id="comment-content" name="content" maxlength="1000" required placeholder="서로를 배려하는 따뜻한 댓글을 남겨주세요." rows="3"></textarea><div class="form-end"><span class="muted">불쾌한 표현은 자동으로 마스킹돼요.</span><button class="button" type="submit">댓글 등록</button></div></form>` : `<button class="login-prompt" data-action="login">로그인하고 댓글을 남겨보세요 →</button>`}</section>`;
}
function writeView() {
  const p = state.posts.find(p => p.id === editingId);
  return `<button class="back-link" data-action="board">${icon('arrow')} 목록으로</button><section class="editor"><div class="eyebrow">A NEW NOTE</div><h1>${p ? '이야기 수정하기' : '어떤 이야기를 나눠볼까요?'}</h1><p class="subtitle">당신의 일상을 편안하게 적어주세요.</p><form id="post-form"><label for="post-title">제목</label><input id="post-title" name="title" maxlength="100" required placeholder="이야기의 제목을 입력해 주세요" value="${esc(p?.title || '')}"><label for="post-content">내용</label><textarea id="post-content" name="content" maxlength="10000" rows="14" required placeholder="오늘의 생각을 자유롭게 남겨보세요.">${esc(p?.content || '')}</textarea><div class="form-end"><span class="muted">${icon('shield')} 불쾌한 표현은 게시 후 자동으로 마스킹됩니다.</span><div><button type="button" class="button secondary" data-action="cancel-edit">취소</button> <button class="button" type="submit">${p ? '수정 완료' : '글 등록하기'}</button></div></div><p class="form-error" role="alert"></p></form></section>`;
}
function adminView() {
  if (user()?.role !== 'admin') { view = 'board'; return boardView(); }
  return `<section class="page-heading"><div class="eyebrow">COMMUNITY CARE</div><h1>금칙어 관리</h1><p class="subtitle">등록한 키워드는 제목·본문·댓글·닉네임에서 별표(*)로 표시됩니다.</p></section><section class="admin-panel"><h2>마스킹 키워드 <span class="count-badge">${state.keywords.length}</span></h2><form id="keyword-form" class="inline-form"><input name="keyword" maxlength="30" required aria-label="추가할 금칙어" placeholder="추가할 키워드 (최대 30자)"><button class="button" type="submit">${icon('plus')} 추가</button></form><p class="muted">대소문자, 글자 사이의 공백·숫자·일부 기호 변형도 함께 감지합니다.</p><div class="keyword-list">${state.keywords.map((k, i) => `<span class="keyword">${esc(k)}<button data-action="remove-keyword" data-index="${i}" aria-label="${esc(k)} 삭제">×</button></span>`).join('')}</div><hr><h2>마스킹 미리보기</h2><label for="filter-test">문장을 입력해 필터를 확인하세요</label><textarea id="filter-test" rows="3" placeholder="미리보기할 문장을 입력하세요"></textarea><output id="filter-output" class="filter-output">마스킹 결과가 여기에 표시됩니다.</output><hr><h2>초기 구성 참고 자료</h2><p class="muted">조사일: 2026-10-27. 공개 자료를 참고해 선정한 소규모 데모 키워드입니다. 포괄적이거나 자동 갱신되는 사전은 아니며, 문맥에 따른 오탐은 관리자가 조정할 수 있습니다.</p><div class="source-links"><a href="https://github.com/Xim-ya/korean_profanity_filter" target="_blank" rel="noopener noreferrer">한국어 욕설 필터 구현 및 예시 ↗</a><a href="https://www.kiso.or.kr/wp-content/uploads/2025/07/KISO-%EB%B3%B4%EB%8F%84%EC%9E%90%EB%A3%8C-KISO-%EC%9A%95%EC%84%A4%EB%B0%A9%EC%A7%80%EC%8B%9C%EC%8A%A4%ED%85%9C%EC%97%90-%EB%84%A4%EC%9D%B4%ED%8A%B8-DB-%EC%B6%94%EA%B0%80_250711.pdf" target="_blank" rel="noopener noreferrer">KISO 욕설방지시스템 운영 자료 (2025) ↗</a></div></section>`;
}
function authDialog(mode = 'login') {
  const signup = mode === 'signup', forgot = mode === 'forgot';
  modal.innerHTML = `<button class="modal-close" data-action="close" aria-label="닫기">×</button><span class="modal-logo">${icon('note')}</span><h2>${signup ? '반가워요, 함께 기록해요' : forgot ? '비밀번호를 잊으셨나요?' : '다시 만나서 반가워요'}</h2><p class="muted">${forgot ? '비밀번호 찾기는 현재 목업으로 제공됩니다.' : '작은 생각이 모여 더 큰 이야기가 되는 곳.'}</p><form id="auth-form" data-mode="${mode}"><label for="email">이메일</label><input id="email" type="email" name="email" autocomplete="email" required maxlength="254" placeholder="hello@example.com">${signup ? '<label for="nickname">닉네임</label><input id="nickname" name="name" required minlength="2" maxlength="20" autocomplete="nickname" placeholder="어떤 이름으로 불러드릴까요?">' : ''}${!forgot ? `<label for="password">비밀번호</label><input id="password" type="password" name="password" required minlength="6" maxlength="100" autocomplete="${signup ? 'new-password' : 'current-password'}" placeholder="6자 이상 입력해 주세요">` : ''}<p class="form-error" role="alert"></p><button class="button full" type="submit">${signup ? '회원가입' : forgot ? '안내 확인' : '로그인'}</button></form>${!forgot ? `<div class="auth-links"><button class="text-button" data-action="${signup ? 'login' : 'signup'}">${signup ? '이미 계정이 있나요? 로그인' : '아직 계정이 없나요? 회원가입'}</button>${!signup ? '<button class="text-button" data-action="forgot">비밀번호 찾기</button>' : ''}</div><div class="demo-box"><span>바로 체험해 보세요</span><div><button class="button secondary small" data-action="demo-login">일반 회원</button><button class="button secondary small" data-action="admin-login">관리자</button></div></div>` : '<button class="text-button full" data-action="login">로그인으로 돌아가기</button>'}<p class="mock-warning">목업 데모 · 데이터와 비밀번호는 이 브라우저에 저장됩니다.<br>실제 사용하는 비밀번호는 입력하지 마세요.</p>`;
  if (!modal.open) modal.showModal();
}
function loginAs(email, password) {
  const account = state.users.find(u => u.email.toLowerCase() === email.toLowerCase() && u.password === password);
  if (!account) throw new Error('이메일 또는 비밀번호를 확인해 주세요.');
  state.sessionId = account.id; modal.close(); persistAndRender(`${mask(account.name, state.keywords)} 님, 반갑습니다.`);
}
function confirmDelete(id) {
  const post = state.posts.find(p => p.id === id); requireOwner(post, user());
  modal.innerHTML = `<button class="modal-close" data-action="close" aria-label="닫기">×</button><h2>이 글을 삭제할까요?</h2><p class="muted">글과 댓글이 함께 삭제되며 되돌릴 수 없습니다.</p><div class="form-end"><button class="button secondary" data-action="close">취소</button><button class="button danger" data-action="confirm-delete" data-id="${id}">삭제하기</button></div>`; modal.showModal();
}
document.addEventListener('click', event => {
  const button = event.target.closest('[data-action]'); if (!button) return;
  event.preventDefault();
  const action = button.dataset.action;
  try {
    if (['login', 'signup', 'forgot'].includes(action)) return authDialog(action);
    if (action === 'close') return modal.close();
    if (action === 'demo-login' || action === 'admin-login') return loginAs(action === 'admin-login' ? 'admin@note.demo' : 'demo@note.demo', action === 'admin-login' ? 'admin1234' : 'demo1234');
    if (action === 'logout') { state.sessionId = null; view = 'board'; return persistAndRender('로그아웃했습니다.'); }
    if (action === 'mine' && !user()) return authDialog();
    if (['board', 'mine', 'admin'].includes(action)) return navigate(action);
    if (action === 'page') { page = Number(button.dataset.page); render(); return; }
    if (action === 'detail') { selectedId = button.dataset.id; view = 'detail'; render(); window.scrollTo(0, 0); return; }
    if (action === 'new') { if (!user()) return authDialog(); editingId = null; view = 'write'; render(); return; }
    if (action === 'edit') { const post = state.posts.find(p => p.id === button.dataset.id); requireOwner(post, user()); editingId = post.id; view = 'write'; render(); return; }
    if (action === 'cancel-edit') { view = editingId ? 'detail' : 'board'; render(); return; }
    if (action === 'delete') return confirmDelete(button.dataset.id);
    if (action === 'confirm-delete') { const post = state.posts.find(p => p.id === button.dataset.id); requireOwner(post, user()); state.posts = state.posts.filter(p => p.id !== post.id); modal.close(); view = 'board'; return persistAndRender('글이 삭제되었습니다.'); }
    if (action === 'remove-keyword') { if (user()?.role !== 'admin') throw new Error('관리자만 변경할 수 있습니다.'); state.keywords.splice(Number(button.dataset.index), 1); persistAndRender('키워드를 삭제했습니다.'); }
  } catch (error) { toast(error.message); }
});
document.addEventListener('submit', event => {
  event.preventDefault(); const form = event.target, data = new FormData(form);
  try {
    if (form.id === 'search-form') { search = String(data.get('search')).trim(); page = 1; render(); }
    if (form.id === 'auth-form') {
      const email = String(data.get('email')).trim(), password = String(data.get('password') || '');
      if (form.dataset.mode === 'forgot') { form.innerHTML = '<div class="mock-result"><strong>목업 안내</strong><p>실제 이메일은 전송되지 않았으며 비밀번호도 변경되지 않았습니다.</p><p>데모 계정: demo@note.demo<br>비밀번호: demo1234</p></div>'; return; }
      if (form.dataset.mode === 'signup') {
        const name = String(data.get('name')).trim(); validateRegistration(state.users, email, name, password);
        const account = { id: crypto.randomUUID(), email: email.toLowerCase(), name, password, role: 'member' };
        state.users.push(account); state.sessionId = account.id; modal.close(); persistAndRender('가입을 환영합니다. 첫 이야기를 남겨보세요.');
      } else loginAs(email, password);
    }
    if (form.id === 'post-form') {
      if (!user()) throw new Error('로그인이 필요합니다.');
      const title = String(data.get('title')).trim(), content = String(data.get('content')).trim();
      if (!title || !content) throw new Error('제목과 내용을 모두 입력해 주세요.');
      if (title.length > 100 || content.length > 10000) throw new Error('제목은 100자, 내용은 10,000자 이내로 입력해 주세요.');
      if (editingId) { const post = state.posts.find(p => p.id === editingId); requireOwner(post, user()); Object.assign(post, { title, content, updatedAt: new Date().toISOString() }); selectedId = post.id; }
      else { const post = { id: crypto.randomUUID(), title, content, authorId: user().id, createdAt: new Date().toISOString(), comments: [] }; state.posts.unshift(post); selectedId = post.id; }
      view = 'detail'; editingId = null; persistAndRender('이야기를 저장했습니다.');
    }
    if (form.id === 'comment-form') {
      if (!user()) throw new Error('로그인이 필요합니다.');
      const content = String(data.get('content')).trim(); if (!content || content.length > 1000) throw new Error('댓글은 1~1,000자로 입력해 주세요.');
      const post = state.posts.find(p => p.id === selectedId); post.comments.push({ id: crypto.randomUUID(), authorId: user().id, content, createdAt: new Date().toISOString() }); persistAndRender('댓글을 등록했습니다.');
    }
    if (form.id === 'keyword-form') {
      if (user()?.role !== 'admin') throw new Error('관리자만 변경할 수 있습니다.');
      const keyword = String(data.get('keyword')).normalize('NFKC').trim().toLowerCase();
      if (!keyword || keyword.length > 30) throw new Error('키워드는 1~30자로 입력해 주세요.');
      if (state.keywords.some(k => k.toLowerCase() === keyword)) throw new Error('이미 등록된 키워드입니다.');
      state.keywords.push(keyword); persistAndRender('키워드를 추가했습니다. 기존 글에도 즉시 적용됩니다.');
    }
  } catch (error) { const field = form.querySelector('.form-error'); if (field) field.textContent = error.message; else toast(error.message); }
});
document.addEventListener('input', event => { if (event.target.id === 'filter-test') document.querySelector('#filter-output').textContent = mask(event.target.value, state.keywords) || '마스킹 결과가 여기에 표시됩니다.'; });
modal.addEventListener('click', event => { if (event.target === modal) { const r = modal.getBoundingClientRect(); if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) modal.close(); } });
render();
