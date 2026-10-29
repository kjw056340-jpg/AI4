'use strict';
const $ = (selector, root = document) => root.querySelector(selector);
const main = $('#main');
const params = new URLSearchParams(location.search);
const page = document.body.dataset.page;
let user = null;
let csrf = '';
let toastTimer;
const won = amount => `${Number(amount).toLocaleString('ko-KR')}원`;
const escapeHTML = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const image = key => `/static/images/${['mug','lamp','chair','bag','clock','vase'].includes(key) ? key : 'mug'}.svg`;
const here = () => location.pathname + location.search;
function loginURL(next = here()) { return '/login?next=' + encodeURIComponent(next); }
function toast(message) {
  $('#toast').textContent = message; $('#toast').hidden = false;
  clearTimeout(toastTimer); toastTimer = setTimeout(() => { $('#toast').hidden = true; }, 4000);
}
function displayError(error, target = $('#form-error')) {
  if (target) { target.textContent = error.message; target.hidden = false; target.setAttribute('role', 'alert'); }
  else toast(error.message);
}
async function api(path, {method = 'GET', data, redirect = true} = {}) {
  if (method !== 'GET' && !csrf) csrf = (await api('/csrf', {redirect:false})).csrf_token;
  const response = await fetch('/api' + path, {
    method, credentials:'same-origin',
    headers: {'Content-Type':'application/json', ...(method !== 'GET' ? {'X-CSRF-Token':csrf} : {})},
    ...(data !== undefined ? {body:JSON.stringify(data)} : {})
  });
  const result = await response.json().catch(() => ({}));
  if (!response.ok) {
    if (response.status === 401 && redirect) { location.assign(loginURL()); throw new Error('로그인이 필요합니다.'); }
    let message = result.detail || '요청을 처리하지 못했습니다.';
    if (result.errors?.length) message += ' ' + result.errors.map(e => e.message).join(' ');
    throw new Error(message);
  }
  return result;
}
async function busy(button, task) {
  if (button.disabled) return;
  button.disabled = true; button.setAttribute('aria-busy','true');
  const errorBox = $('#form-error'); if (errorBox) errorBox.hidden = true;
  try { await task(); } catch (error) { displayError(error); }
  finally { if (button.isConnected) { button.disabled = false; button.removeAttribute('aria-busy'); } }
}
function requireLogin() {
  if (user) return true;
  location.assign(loginURL()); return false;
}
async function refreshCart() {
  if (!user) return;
  const cart = await api('/cart');
  $('#cart-count').textContent = cart.items.reduce((n,i) => n + i.quantity, 0);
}
function heading(title, text) { return `<h1 class="page-title">${title}</h1><p class="page-subtitle">${text}</p>`; }
function empty(title, text, href='/products', label='상품 둘러보기') {
  return `<div class="empty"><p class="eyebrow">A LITTLE PAUSE</p><h2>${title}</h2><p>${text}</p><a class="button" href="${href}">${label} →</a></div>`;
}
function pagination(current, more, build) {
  if (current === 1 && !more) return '';
  return `<nav class="pagination" aria-label="페이지 이동">${current > 1 ? `<a class="button secondary small" href="${build(current-1)}">이전</a>` : ''}<span>${current} 페이지</span>${more ? `<a class="button secondary small" href="${build(current+1)}">다음</a>` : ''}</nav>`;
}
function field(name, label, {type='text',value='',required=false,max=300,autocomplete='',min} = {}) {
  return `<div class="field"><label for="${name}">${label}</label><input id="${name}" name="${name}" type="${type}" value="${escapeHTML(value)}" maxlength="${max}" ${required ? 'required' : ''} ${autocomplete ? `autocomplete="${autocomplete}"` : ''} ${min ? `minlength="${min}"` : ''}></div>`;
}
function formError() { return '<div id="form-error" class="error" role="alert" hidden></div>'; }
function productCard(p) {
  return `<article class="product-card"><a href="/product?id=${encodeURIComponent(p.id)}"><div class="product-image"><img src="${image(p.image_key)}" alt="${escapeHTML(p.name)}" loading="lazy" width="400" height="360"><span class="tag">${p.stock ? 'ONDO SELECT' : 'SOLD OUT'}</span></div><h3>${escapeHTML(p.name)}</h3><div class="category">${escapeHTML(p.category)}</div><div class="card-bottom"><span class="price">${won(p.price)}</span><span>${p.stock ? '자세히 보기 ↗' : '품절'}</span></div></a></article>`;
}
async function catalog() {
  const category = params.get('category') || '';
  const current = Math.max(1, Number(params.get('page')) || 1);
  const q = new URLSearchParams({page:current}); if (category) q.set('category',category);
  const result = await api('/products?' + q);
  main.innerHTML = `<div class="container"><section class="hero"><div class="hero-copy"><p class="eyebrow">LITTLE THINGS, BETTER DAYS</p><h1>일상에 더하는<br>기분 좋은 <em>온도.</em></h1><p>오래 곁에 두고 싶은 물건들.<br>당신의 보통 날을 조금 더 특별하게 만들어 보세요.</p><a class="button" href="#collection">취향을 발견하기 <span>↗</span></a></div><div class="hero-art" aria-hidden="true"><img class="vase" src="/static/images/vase.svg" alt=""><img class="mug" src="/static/images/mug.svg" alt=""><span class="hero-caption">OBJECTS FOR YOUR EVERYDAY</span></div></section><section id="collection"><div class="section-heading"><div><p class="eyebrow">CURATED FOR YOU</p><h2>오늘의 좋은 발견</h2><p>작은 디테일에서 시작되는 일상의 즐거움.</p></div><small>온도의 셀렉션</small></div><nav class="filters" aria-label="상품 카테고리">${['','리빙','키친','가구','라이프'].map(c=>`<a class="filter ${c===category?'active':''}" ${c===category?'aria-current="page"':''} href="/products${c?'?category='+encodeURIComponent(c):''}#collection">${c||'전체'}</a>`).join('')}</nav><div class="product-grid">${result.items.map(productCard).join('')}</div>${!result.items.length?empty('아직 준비 중인 컬렉션입니다.','다른 카테고리도 둘러보세요.'):''}${pagination(current,result.has_more,n=>'/products?'+new URLSearchParams({page:n,category}))}</section><section class="benefits" aria-label="쇼핑 안내"><div><strong><span>↗</span>전 상품 무료배송</strong><p>작은 물건 하나도 부담 없이 만나보세요.</p></div><div><strong><span>◇</span>취향을 담은 큐레이션</strong><p>매일의 쓰임과 오래가는 아름다움을 생각합니다.</p></div><div><strong><span>☼</span>일상의 좋은 온도</strong><p>당신의 공간에 따뜻한 변화를 더해요.</p></div></section></div>`;
  if (location.hash === '#collection') $('#collection').scrollIntoView();
}
async function detail() {
  const id = params.get('id'); if (!id) throw new Error('상품을 선택해 주세요.');
  const p = await api('/products/' + encodeURIComponent(id));
  main.innerHTML = `<div class="container"><p class="breadcrumb"><a href="/products">Shop</a> / ${escapeHTML(p.category)} / ${escapeHTML(p.name)}</p><div class="detail-layout"><div class="detail-image"><img src="${image(p.image_key)}" alt="${escapeHTML(p.name)}"></div><section class="detail-copy"><p class="eyebrow">ONDO ORIGINAL SELECTION</p><h1>${escapeHTML(p.name)}</h1><div class="detail-price">${won(p.price)}</div><p class="description">${escapeHTML(p.description)}</p><hr class="divider"><div class="summary-row"><span>배송비</span><span>무료배송</span></div><div class="summary-row"><span>재고</span><span>${p.stock}개</span></div><div class="quantity-row"><label for="quantity">구매 수량</label><input id="quantity" type="number" min="1" max="${Math.min(99,p.stock)||1}" value="1" ${p.stock?'':'disabled'}></div>${formError()}<div class="actions"><button id="add-cart" class="button secondary" ${p.stock?'':'disabled'}>장바구니 담기</button><button id="buy-now" class="button" ${p.stock?'':'disabled'}>${p.stock?'바로 구매하기':'품절'}</button></div><p class="help">이미지는 상품 이해를 돕기 위한 일러스트입니다.</p></section></div></div>`;
  function quantity() { const n=Number($('#quantity').value); if(!Number.isInteger(n)||n<1||n>Math.min(99,p.stock)) throw new Error('구매 수량을 확인해 주세요.'); return n; }
  $('#add-cart').onclick = event => busy(event.currentTarget, async () => {
    if (!requireLogin()) return;
    await api('/cart/items',{method:'POST',data:{product_id:id,quantity:quantity()}});
    await refreshCart(); toast('장바구니에 담았습니다.');
  });
  $('#buy-now').onclick = event => busy(event.currentTarget, async () => {
    const qty=quantity();
    const target='/checkout?'+new URLSearchParams({source:'direct',product_id:id,quantity:qty});
    if (!user) { location.assign(loginURL(target)); return; }
    location.assign(target);
  });
}
async function authForm(register = false) {
  const next = params.get('next') || '/products';
  main.innerHTML = `<div class="container"><section class="form-card"><p class="eyebrow">WELCOME TO ONDO</p><h1>${register?'온도와 함께 시작해요':'다시 만나 반가워요'}</h1><p class="subtitle">${register?'나만의 취향을 발견하는 첫걸음.':'좋아하는 물건이 기다리고 있어요.'}</p><form id="auth-form">${field('email','이메일',{type:'email',required:true,max:254,autocomplete:'email'})}${field('password','비밀번호',{type:'password',required:true,max:72,min:register?10:1,autocomplete:register?'new-password':'current-password'})}${register?'<p class="help">문자·숫자 포함 10자 이상, 한글 포함 시 72바이트 이하</p>'+field('name','이름',{required:true,max:60,autocomplete:'name'})+field('phone','연락처 (선택)',{type:'tel',max:30,autocomplete:'tel'})+field('address','주소 (선택)',{max:300,autocomplete:'street-address'}):''}${formError()}<button class="button wide" type="submit">${register?'회원가입':'로그인'} →</button></form><p class="form-switch">${register?'이미 회원이신가요?':'처음 방문하셨나요?'} <a href="/${register?'login':'register'}?next=${encodeURIComponent(next)}">${register?'로그인':'회원가입'}</a></p></section></div>`;
  $('#auth-form').onsubmit = event => { event.preventDefault(); busy($('button[type=submit]',event.currentTarget),async()=>{
    const data = Object.fromEntries(new FormData($('#auth-form')));
    const result = await api('/auth/'+(register?'register':'login')+'?next='+encodeURIComponent(next),{method:'POST',data,redirect:false});
    // 회원가입 후에도 서버가 next를 검사하는 로그인 흐름과 동일한 안전한 경로만 허용합니다.
    if(register) {
      const parsed = new URL(next,location.origin);
      const allowed=['/products','/product','/cart','/checkout','/account','/orders'];
      location.assign(parsed.origin===location.origin&&allowed.includes(parsed.pathname)?parsed.pathname+parsed.search:'/products');
    } else location.assign(result.next);
  }); };
}
function lineItem(i, editable=false) {
  const p=i.product;
  return `<div class="line-item"><img class="line-image" src="${image(p?.image_key)}" alt=""><div><h3><a href="/product?id=${encodeURIComponent(i.product_id)}">${escapeHTML(i.product_name)}</a></h3><p>${won(i.unit_price)} · ${i.quantity}개</p><strong>${won(i.unit_price*i.quantity)}</strong>${editable?`<div class="line-actions"><label class="help" for="qty-${i.product_id}">수량</label><input id="qty-${i.product_id}" type="number" value="${i.quantity}" min="1" max="99"><button class="text-button" data-update="${i.product_id}">변경</button><button class="text-button" data-remove="${i.product_id}">삭제</button></div>${!p?.is_active||p.stock<i.quantity?'<p class="error">판매 상태 또는 재고를 확인해 주세요.</p>':''}`:''}</div></div>`;
}
async function cartPage() {
  const cart=await api('/cart');
  main.innerHTML=`<div class="container">${heading('장바구니','당신의 일상에 함께할 물건들.')}<div id="cart-content">${cart.items.length?`<div class="cart-layout"><section>${cart.items.map(i=>lineItem(i,true)).join('')}${formError()}</section><aside class="summary"><h2>주문 예상 금액</h2><div class="summary-row"><span>상품 금액</span><span>${won(cart.total_amount)}</span></div><div class="summary-row"><span>배송비</span><span>무료</span></div><div class="summary-row total"><span>합계</span><span>${won(cart.total_amount)}</span></div><a class="button wide" href="/checkout?source=cart">주문하기 →</a><p class="help">가격과 재고는 주문 생성 시 다시 확인합니다.</p></aside></div>`:empty('장바구니가 비어 있어요.','마음에 드는 물건을 담아보세요.')}</div></div>`;
  document.querySelectorAll('[data-update]').forEach(button=>button.onclick=()=>busy(button,async()=>{
    const id=button.dataset.update; const quantity=Number(document.getElementById('qty-'+id).value);
    if(!Number.isInteger(quantity)||quantity<1||quantity>99) throw new Error('수량은 1~99개로 입력해 주세요.');
    await api('/cart/items/'+id,{method:'PATCH',data:{quantity}}); await cartPage(); await refreshCart();
  }));
  document.querySelectorAll('[data-remove]').forEach(button=>button.onclick=()=>busy(button,async()=>{
    await api('/cart/items/'+button.dataset.remove,{method:'DELETE'}); await cartPage(); await refreshCart();
  }));
}
function shippingFields() {
  return field('recipient','받는 분',{value:user.name,required:true,max:60,autocomplete:'name'})+
    field('phone','연락처',{value:user.phone,type:'tel',required:true,max:30,min:7,autocomplete:'tel'})+
    field('address','배송지 주소',{value:user.address,required:true,max:300,min:5,autocomplete:'street-address'});
}
async function checkoutPage() {
  let order=null, items=[], total=0;
  const orderId=params.get('order_id');
  const source=params.get('source')||'cart';
  const productId=params.get('product_id');
  const quantity=Number(params.get('quantity')||1);
  if(orderId) { order=await api('/orders/'+encodeURIComponent(orderId)); items=order.items; total=order.total_amount; }
  else if(source==='direct') {
    if(!productId||!Number.isInteger(quantity)||quantity<1||quantity>99) throw new Error('구매할 상품과 수량을 확인해 주세요.');
    const p=await api('/products/'+encodeURIComponent(productId));
    items=[{product_id:p.id,product_name:p.name,unit_price:p.price,quantity,product:p}]; total=p.price*quantity;
  } else { const cart=await api('/cart'); items=cart.items; total=cart.total_amount; }
  if(!items.length) { main.innerHTML=`<div class="container">${empty('주문할 상품이 없습니다.','장바구니에 상품을 담아 주세요.')}</div>`; return; }
  if(order&&order.status!=='ORDERED') { main.innerHTML=`<div class="container">${empty(order.status==='PAID'?'이미 결제된 주문입니다.':'취소된 주문입니다.','구매내역에서 주문 상태를 확인할 수 있습니다.','/orders','구매내역 보기')}</div>`;return; }
  main.innerHTML=`<div class="container">${heading('주문 / 결제','받으실 곳을 확인하고, 일상의 좋은 물건을 만나보세요.')}<form id="checkout-form"><div class="checkout-layout"><div><section class="panel"><h2>주문 상품</h2>${items.map(i=>lineItem(i)).join('')}</section><section class="panel"><h2>배송 정보</h2>${order?`<p>${escapeHTML(order.recipient)} · ${escapeHTML(order.phone)}</p><p>${escapeHTML(order.address)}</p>`:shippingFields()}</section><div class="notice">모의 결제입니다. 카드 정보 입력이나 실제 금액 청구는 없습니다.</div></div><aside class="summary"><h2>결제 금액</h2><div class="summary-row"><span>상품 금액</span><span>${won(total)}</span></div><div class="summary-row"><span>배송비</span><span>무료</span></div><div class="summary-row total"><span>총 결제 금액</span><span>${won(total)}</span></div>${formError()}${order?'<label class="checkline"><input type="checkbox" required><span>주문 내용을 확인했으며 모의 결제에 동의합니다.</span></label>':'<p class="help">주문을 확정하면 최종 가격을 확인한 후 결제할 수 있습니다.</p>'}<button class="button wide" type="submit">${order?'모의 결제하기':'주문 확정 · 금액 확인'} →</button><a class="button secondary wide" href="/cart">장바구니 보기</a></aside></div></form></div>`;
  $('#checkout-form').onsubmit=event=>{event.preventDefault();busy($('button[type=submit]',event.currentTarget),async()=>{
    if(!order) {
      const data={...Object.fromEntries(new FormData($('#checkout-form'))),source};
      if(source==='direct') {data.product_id=productId;data.quantity=quantity;}
      order=await api('/orders/checkout',{method:'POST',data});
      // URL에 서버 주문번호를 먼저 저장해 새로고침/로그인 복귀/결제 재시도를 안전하게 합니다.
      location.replace('/checkout?order_id='+encodeURIComponent(order.id)); return;
    }
    const keyName='ondo-payment-'+order.id;
    let key=sessionStorage.getItem(keyName);
    if(!key){key=crypto.randomUUID();sessionStorage.setItem(keyName,key);}
    await api('/payments',{method:'POST',data:{order_id:order.id,idempotency_key:key}});
    sessionStorage.removeItem(keyName);sessionStorage.setItem('ondo-flash','결제가 완료되었습니다. 구매내역에서 확인해 보세요.');
    location.replace('/products');
  });};
}
async function accountPage() {
  main.innerHTML=`<div class="container">${heading('마이 온도','회원정보를 관리하고 지난 취향을 돌아보세요.')}<nav class="account-menu"><a href="/account">회원정보</a><a href="/orders">구매내역 →</a></nav><div class="account-layout"><section class="panel"><h2>회원정보 수정</h2><p class="help">로그인 이메일: ${escapeHTML(user.email)}</p><form id="profile-form">${field('name','이름',{value:user.name,required:true,max:60,autocomplete:'name'})}${field('phone','연락처',{value:user.phone,type:'tel',max:30,autocomplete:'tel'})}${field('address','주소',{value:user.address,max:300,autocomplete:'street-address'})}<hr class="divider"><p class="help">비밀번호를 변경할 때만 아래 두 항목을 입력해 주세요.</p>${field('current_password','현재 비밀번호',{type:'password',max:72,autocomplete:'current-password'})}${field('new_password','새 비밀번호',{type:'password',max:72,autocomplete:'new-password'})}<p class="help">새 비밀번호: 문자·숫자 포함 10자 이상, UTF-8 72바이트 이하</p>${formError()}<button class="button" type="submit">변경사항 저장</button></form></section><aside><div class="panel"><h2>나의 구매내역</h2><p class="help">결제한 상품과 주문 상태를 확인하세요.</p><a class="button secondary wide" href="/orders">구매내역 보기 →</a></div><section class="panel danger-zone"><h2>회원 탈퇴</h2><p class="help">탈퇴하면 복구할 수 없습니다. 개인정보는 익명화하고 주문·결제 기록을 보존합니다. 미결제 주문은 취소됩니다.</p><form id="delete-form">${field('delete_password','비밀번호 확인',{type:'password',required:true,max:72,autocomplete:'current-password'})}<label class="checkline"><input type="checkbox" required><span>안내 내용을 확인했으며 탈퇴에 동의합니다.</span></label><div id="delete-error" class="error" role="alert" hidden></div><button class="button danger wide" type="submit">회원 탈퇴</button></form></section></aside></div></div>`;
  $('#profile-form').onsubmit=event=>{event.preventDefault();busy($('button[type=submit]',event.currentTarget),async()=>{
    const data=Object.fromEntries(new FormData($('#profile-form')));
    if(!data.new_password){delete data.new_password;delete data.current_password;}
    user=await api('/me',{method:'PATCH',data});await accountPage();toast('회원정보를 저장했습니다.');
  });};
  $('#delete-form').onsubmit=event=>{event.preventDefault();const button=$('button[type=submit]',event.currentTarget);busy(button,async()=>{
    try {await api('/me',{method:'DELETE',data:{password:$('#delete_password').value}});sessionStorage.setItem('ondo-flash','탈퇴가 완료되었습니다.');location.replace('/products');}
    catch(error){displayError(error,$('#delete-error'));}
  });};
}
async function ordersPage() {
  const current=Math.max(1,Number(params.get('page'))||1);
  const result=await api('/orders?page='+current);
  const statuses={ORDERED:'결제 대기',PAID:'결제 완료',CANCELED:'취소 완료'};
  main.innerHTML=`<div class="container">${heading('구매내역','당신의 일상에 더해진 좋은 물건들.')}<nav class="account-menu"><a href="/account">← 회원정보</a><a href="/products">상품 둘러보기</a></nav>${result.items.length?result.items.map(o=>`<article class="order-card"><div class="order-head"><div><strong>${new Date(o.created_at).toLocaleDateString('ko-KR')}</strong><br><small>주문번호 ${escapeHTML(o.id)}</small></div><span class="status ${o.status==='PAID'?'paid':''}">${statuses[o.status]||escapeHTML(o.status)}</span></div>${o.items.map(i=>lineItem(i)).join('')}<div class="order-foot"><strong>총 ${won(o.total_amount)}</strong>${o.status==='ORDERED'?`<div class="actions"><a class="button small" href="/checkout?order_id=${encodeURIComponent(o.id)}">결제 이어하기</a><button class="button secondary small" data-cancel="${o.id}">주문 취소</button></div>`:`<span class="help">${o.payment?'모의 결제 · '+escapeHTML(o.payment.id):'취소된 주문입니다.'}</span>`}</div></article>`).join(''):empty('아직 구매내역이 없습니다.','마음에 드는 상품으로 첫 번째 취향을 채워보세요.')}${pagination(current,result.has_more,n=>'/orders?page='+n)}</div>`;
  document.querySelectorAll('[data-cancel]').forEach(button=>button.onclick=()=>busy(button,async()=>{
    await api('/orders/'+button.dataset.cancel+'/cancel',{method:'POST'});await ordersPage();toast('주문이 취소되었습니다.');
  }));
}
async function start() {
  try {
    user=await api('/me',{redirect:false}).catch(error=>{if(error.message.includes('로그인'))return null;throw error;});
    if(user){$('#account-link').textContent='마이 온도';$('#account-link').href='/account';$('#logout').hidden=false;await refreshCart();}
    $('#logout').onclick=event=>busy(event.currentTarget,async()=>{
      await api('/auth/logout',{method:'POST'});sessionStorage.setItem('ondo-flash','로그아웃했습니다.');location.replace('/products');
    });
    if(['cart','checkout','account','orders'].includes(page)&&!requireLogin())return;
    const renderers={products:catalog,product:detail,login:()=>authForm(false),register:()=>authForm(true),cart:cartPage,checkout:checkoutPage,account:accountPage,orders:ordersPage};
    await renderers[page]();
    const flash=sessionStorage.getItem('ondo-flash');if(flash){sessionStorage.removeItem('ondo-flash');toast(flash);}
  } catch(error) {
    main.innerHTML=`<div class="container">${heading('잠시 확인이 필요해요','아래 안내를 확인하고 다시 시도해 주세요.')}<div class="error" role="alert">${escapeHTML(error.message)}</div><a class="button" href="${escapeHTML(here())}">다시 시도</a> <a class="button secondary" href="/products">상품목록</a></div>`;
  }
}
start();
