export const STORAGE_KEY = 'note-demo-v1';
export const PAGE_SIZE = 10;
export const initialKeywords = ['씨발', '시발', '씨벌', '개새끼', '병신', '븅신', '지랄', '존나', '좆', 'ㅅㅂ', 'ㅆㅂ', 'ㅂㅅ', 'fuck', 'shit'];
export function mask(text, keywords) {
  let result = String(text ?? '').normalize('NFKC');
  for (const keyword of [...keywords].sort((a, b) => b.length - a.length)) {
    const escaped = [...keyword.normalize('NFKC')].map(c => c.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('[\\s._*\\-0-9]*');
    if (!escaped) continue;
    // English words use boundaries to avoid masking words such as "shift".
    const source = /^[a-z]+$/i.test(keyword) ? `\\b${escaped}\\b` : escaped;
    result = result.replace(new RegExp(source, 'giu'), match => '*'.repeat([...match].length));
  }
  return result;
}
export function validateRegistration(users, email, name, password) {
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) throw new Error('올바른 이메일 주소를 입력해 주세요.');
  if (users.some(u => u.email.toLowerCase() === email.toLowerCase())) throw new Error('이미 가입된 이메일입니다.');
  if (name.trim().length < 2 || name.trim().length > 20) throw new Error('닉네임은 2~20자로 입력해 주세요.');
  if (password.length < 6 || password.length > 100) throw new Error('비밀번호는 6~100자로 입력해 주세요.');
}
export function requireOwner(post, user) {
  if (!user || post.authorId !== user.id) throw new Error('작성자만 글을 수정하거나 삭제할 수 있습니다.');
}
export function paginate(items, page, size = PAGE_SIZE) {
  const pages = Math.max(1, Math.ceil(items.length / size));
  const current = Math.min(Math.max(1, page), pages);
  return { items: items.slice((current - 1) * size, current * size), pages, current };
}
export function createInitialState() {
  const titles = [
    '작은 기록이 일상을 바꾸는 순간', '요즘 여러분은 어떤 책을 읽고 있나요?', '집중이 안 되는 날, 나만의 리셋 방법',
    '퇴근 후 30분, 나를 위한 시간을 만들었어요', '이번 주말에는 조금 느리게 걸어보려고요', '처음으로 혼자 떠난 여행에서 배운 것들',
    '좋아하는 공간을 소개해 주세요 ☕', '매일 한 줄씩, 감사 일기를 시작했습니다', '오래된 플레이리스트를 다시 들으며', '잘하지 않아도 계속하는 마음',
    '아침을 기분 좋게 시작하는 작은 습관', '가을 산책길에서 만난 풍경', '서로에게 다정한 말을 건네는 하루',
    '이번 달에 꼭 해보고 싶은 일', '나만의 작업 공간을 정리했어요', '처음 만들어 본 홈메이드 파스타',
    '생각이 많을 때는 종이에 적어 보세요', '오늘 발견한 소소한 행복', '오랜 친구와 나눈 짧은 대화',
    '새로운 취미를 찾고 있어요', '비 오는 날 듣기 좋은 음악', '올해 가장 기억에 남는 순간', '반갑습니다, 첫 인사를 남겨요!'
  ];
  const names = ['서연', '지우', '하루', '민준', '느린산책', '다온'];
  const users = names.map((name, i) => ({ id: `user-${i}`, email: i === 0 ? 'demo@note.demo' : `member${i}@note.demo`, name, password: 'demo1234', role: 'member' }));
  users.push({ id: 'admin', email: 'admin@note.demo', name: '노트 관리자', password: 'admin1234', role: 'admin' });
  const base = Date.now();
  const posts = titles.map((title, i) => ({
    id: `post-${i}`, title, content: i === 0 ? '언젠가부터 하루의 끝에 작은 기록을 남기기 시작했어요.\n\n거창한 계획이나 특별한 이야기는 아니에요. 오늘 마신 커피의 향, 우연히 들은 좋은 말, 집으로 돌아오는 길의 하늘 같은 것들이요.\n\n차곡차곡 쌓인 문장을 다시 읽다 보니, 평범하다고 생각했던 날들도 저마다의 색을 가지고 있더라고요.\n\n여러분은 오늘 어떤 순간을 기억하고 싶으신가요?' : `${title.replace(/[?☕!]/g, '')}.\n\n일상 속에서 떠오른 생각을 이곳에 남겨봅니다. 작은 경험을 나누는 것만으로도 누군가에게는 새로운 시작이 될 수 있겠죠.\n\n여러분의 이야기도 댓글로 들려주세요. 함께 나누고 싶어요.`,
    authorId: users[i % names.length].id, createdAt: new Date(base - i * 3600000 * 5).toISOString(),
    comments: i < 9 ? [{ id: `comment-${i}`, authorId: users[(i + 1) % names.length].id, content: '이야기 나눠주셔서 감사해요. 저도 오늘부터 작은 기록을 시작해 볼게요 🌿', createdAt: new Date(base - i * 3600000 * 5 + 1000).toISOString() }] : []
  }));
  return { version: 1, users, posts, keywords: initialKeywords, sessionId: null };
}
