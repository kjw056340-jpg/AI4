const $ = (selector) => document.querySelector(selector);
const labels = { blocking: '동기 호출', async: '비동기 호출', thread: '동기 함수 개선' };
let catalog = [];
let running = false;
const records = [];

async function getJSON(url) {
  const response = await fetch(url, { cache: 'no-store', signal: AbortSignal.timeout(30000) });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}

function renderProducts() {
  const count = Number($('#count').value);
  $('#completed').textContent = `0 / ${count}`;
  $('#products').innerHTML = catalog.slice(0, count).map(p => `
    <article class="product" id="product-${p.id}">
      <div class="product-visual" aria-hidden="true">${p.icon}</div>
      <div class="product-body"><span class="category">${p.category}</span>
      <h3>${p.name}</h3><div class="price">${p.price.toLocaleString('ko-KR')}원</div>
      <p class="stock">재고와 배송 정보를 조회해 보세요.</p><div class="product-state">조회 대기</div></div>
    </article>`).join('');
}

function renderHistory() {
  $('#history').innerHTML = records.slice(0, 9).map(r => `<tr>
    <td>${labels[r.mode]}</td><td>${r.count}개 × ${r.delay}초</td>
    <td>${r.total.toFixed(2)}초</td><td>${r.health === null ? '측정 실패' : `${r.health.toFixed(2)}초`}</td>
    <td>${r.completed} / ${r.count}</td></tr>`).join('');
}

async function run(mode) {
  if (running || !catalog.length) return;
  running = true;
  document.querySelectorAll('button, select').forEach(el => { el.disabled = true; });
  $(`[data-mode="${mode}"]`).classList.add('active');
  renderProducts();
  const count = Number($('#count').value);
  const delay = Number($('#delay').value);
  let completed = 0;
  let finished = false;
  let maxHealth = null;
  let healthErrors = 0;
  const start = performance.now();
  $('#run-label').textContent = `${labels[mode]} · ${count}개 상품 × ${delay}초`;
  $('#health').textContent = '대기 중';
  $('#status').className = 'status';
  $('#status').textContent = '상품 조회 요청을 동시에 보냈습니다. 서버 상태도 확인합니다…';
  const timer = setInterval(() => {
    $('#elapsed').textContent = `${((performance.now() - start) / 1000).toFixed(2)} s`;
  }, 50);

  // 한 번에 상태 확인 요청 하나만 전송해 요청이 계속 쌓이지 않게 합니다.
  // 상품 요청은 최대 4개로 제한하여 일반적인 브라우저 연결 제한의 영향을 줄입니다.
  const healthLoop = (async () => {
    await new Promise(resolve => setTimeout(resolve, 150));
    while (!finished) {
      const sent = performance.now();
      $('#health').textContent = '확인 중…';
      try {
        await getJSON(`/api/health?t=${Date.now()}`);
        const seconds = (performance.now() - sent) / 1000;
        maxHealth = Math.max(maxHealth ?? 0, seconds);
        $('#health').textContent = `${maxHealth.toFixed(2)} s`;
      } catch {
        healthErrors += 1;
        $('#health').textContent = '연결 실패';
      }
      if (!finished) await new Promise(resolve => setTimeout(resolve, 400));
    }
  })();

  const tasks = catalog.slice(0, count).map(async p => {
    const card = $(`#product-${p.id}`);
    card.classList.add('pending');
    card.querySelector('.product-state').textContent = '재고 · 배송 정보 조회 중';
    try {
      const data = await getJSON(`/api/products/${p.id}?mode=${mode}&delay=${delay}`);
      const seconds = (performance.now() - start) / 1000;
      completed += 1;
      card.classList.replace('pending', 'done');
      card.querySelector('.stock').textContent = `재고 ${data.product.stock}개 · ${data.product.delivery}`;
      card.querySelector('.product-state').textContent = `${seconds.toFixed(2)}초에 수신 · 서버 처리 ${data.server_seconds.toFixed(2)}초`;
      $('#completed').textContent = `${completed} / ${count}`;
    } catch (error) {
      card.classList.replace('pending', 'failed');
      card.querySelector('.product-state').textContent = `조회 실패 · ${error.name}: ${error.message}`;
    }
  });
  await Promise.all(tasks);
  const total = (performance.now() - start) / 1000;
  finished = true;
  clearInterval(timer);
  $('#elapsed').textContent = `${total.toFixed(2)} s`;
  // 마지막 상태 확인 응답까지 수집한 뒤 기록합니다.
  await healthLoop;
  records.unshift({ mode, count, delay, total, health: maxHealth, completed });
  renderHistory();
  const failed = completed !== count || healthErrors > 0;
  $('#status').className = failed ? 'status error' : 'status';
  $('#status').textContent = failed
    ? '일부 요청에 실패했습니다. 서버 실행 여부와 터미널 로그를 확인해 주세요.'
    : mode === 'blocking'
      ? '조회 완료. 동기 호출이 이벤트 루프를 막아 상품 조회와 서버 상태 확인이 지연되었습니다.'
      : '조회 완료. 대기 시간을 겹쳐 처리하면서 서버 상태 확인 요청에도 응답했습니다.';
  document.querySelectorAll('button, select').forEach(el => { el.disabled = false; });
  $(`[data-mode="${mode}"]`).classList.remove('active');
  running = false;
}

document.querySelectorAll('[data-mode]').forEach(button => {
  button.disabled = true;
  button.addEventListener('click', () => run(button.dataset.mode));
});
$('#count').addEventListener('change', renderProducts);

getJSON('/api/catalog').then(data => {
  catalog = data;
  renderProducts();
  document.querySelectorAll('[data-mode]').forEach(button => { button.disabled = false; });
}).catch(error => {
  $('#status').className = 'status error';
  $('#status').textContent = `상품 목록을 불러오지 못했습니다. 서버를 실행한 후 새로고침해 주세요. (${error.message})`;
});
