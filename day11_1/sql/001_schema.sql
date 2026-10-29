-- 신규 Supabase 프로젝트의 SQL Editor에서 한 번 실행합니다.
-- 기존 테이블을 삭제하거나 덮어쓰지 않습니다. 전체 파일은 한 트랜잭션입니다.
begin;
create table public.users (
  id uuid primary key default gen_random_uuid(),
  email text not null unique check (email = lower(email) and length(email) <= 254),
  password_hash text not null,
  name text not null check (length(name) between 1 and 60),
  phone text not null default '' check (length(phone) <= 30),
  address text not null default '' check (length(address) <= 300),
  token_version integer not null default 0 check (token_version >= 0),
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create table public.products (
  id uuid primary key default gen_random_uuid(),
  name text not null check (length(name) between 1 and 120),
  description text not null,
  category text not null,
  price bigint not null check (price between 1 and 100000000),
  stock integer not null default 0 check (stock >= 0),
  image_key text not null default 'mug' check (image_key in ('mug','lamp','chair','bag','clock','vase')),
  is_active boolean not null default true,
  created_at timestamptz not null default now()
);
create table public.orders (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.users(id) on delete restrict,
  status text not null default 'CART' check (status in ('CART','ORDERED','PAID','CANCELED')),
  total_amount bigint not null default 0 check (total_amount >= 0),
  recipient text not null default '',
  phone text not null default '',
  address text not null default '',
  created_at timestamptz not null default now(),
  ordered_at timestamptz,
  paid_at timestamptz,
  check (status <> 'PAID' or paid_at is not null),
  check (status not in ('ORDERED','PAID') or (total_amount > 0 and ordered_at is not null))
);
-- 사용자당 활성 장바구니는 정확히 최대 하나입니다.
create unique index orders_one_cart on public.orders(user_id) where status = 'CART';
create index orders_user_history on public.orders(user_id, created_at desc);
create table public.order_items (
  id uuid primary key default gen_random_uuid(),
  order_id uuid not null references public.orders(id) on delete cascade,
  product_id uuid not null references public.products(id) on delete restrict,
  product_name text not null,
  unit_price bigint not null check (unit_price between 1 and 100000000),
  quantity integer not null check (quantity between 1 and 99),
  unique (order_id, product_id)
);
create index order_items_product on public.order_items(product_id);
create table public.payments (
  id uuid primary key default gen_random_uuid(),
  order_id uuid not null unique references public.orders(id) on delete restrict,
  user_id uuid not null references public.users(id) on delete restrict,
  amount bigint not null check (amount > 0),
  status text not null default 'SUCCEEDED' check (status = 'SUCCEEDED'),
  method text not null default 'MOCK' check (method = 'MOCK'),
  idempotency_key uuid not null,
  created_at timestamptz not null default now(),
  unique (user_id, idempotency_key)
);
create index payments_user on public.payments(user_id, created_at desc);
create index products_catalog on public.products(category, created_at desc) where is_active;

-- 브라우저의 anon/authenticated 키로 직접 읽거나 쓸 수 없습니다.
alter table public.users enable row level security;
alter table public.products enable row level security;
alter table public.orders enable row level security;
alter table public.order_items enable row level security;
alter table public.payments enable row level security;
revoke all on public.users, public.products, public.orders, public.order_items, public.payments from anon, authenticated;
grant select, insert, update, delete on public.users, public.products, public.orders, public.order_items, public.payments to service_role;

create function public.shop_order_json(p_id uuid) returns jsonb
language sql stable security invoker set search_path = '' as $$
  select to_jsonb(o) || jsonb_build_object('items', coalesce((
    select jsonb_agg(to_jsonb(i) || jsonb_build_object('product', jsonb_build_object(
      'id',p.id,'name',p.name,'price',p.price,'stock',p.stock,'image_key',p.image_key,'is_active',p.is_active)) order by i.id)
    from public.order_items i join public.products p on p.id=i.product_id where i.order_id=o.id
  ), '[]'::jsonb), 'payment', (select to_jsonb(t) from public.payments t where t.order_id=o.id))
  from public.orders o where o.id=p_id;
$$;

-- 모든 사용자 쓰기는 사용자 행 잠금 → 주문 → 상품 UUID 오름차순 잠금 순서입니다.
-- 로그인 이후 탈퇴/비밀번호 변경/로그아웃이 일어난 토큰도 DB 안에서 재검증합니다.
create function public.shop_mutate(p_user uuid, p_version integer, p_action text, p_data jsonb default '{}')
returns jsonb language plpgsql security invoker set search_path = '' as $$
declare
  u public.users; o public.orders; v_product public.products; it record;
  v_id uuid; v_qty integer; v_sum bigint; v_key uuid; v_payment public.payments;
begin
  select * into u from public.users where id=p_user for update;
  if not found or not u.is_active or u.token_version <> p_version then
    raise exception using message='AUTH_REQUIRED', errcode='P0001';
  end if;
  if p_action='logout' then
    update public.users set token_version=token_version+1, updated_at=now() where id=p_user;
    return '{}'::jsonb;
  elsif p_action='profile' then
    update public.users set name=p_data->>'name', phone=p_data->>'phone', address=p_data->>'address',
      password_hash=coalesce(p_data->>'password_hash',password_hash),
      token_version=token_version + case when p_data ? 'password_hash' then 1 else 0 end,
      updated_at=now() where id=p_user returning * into u;
    return to_jsonb(u) - 'password_hash';
  elsif p_action='delete_account' then
    update public.orders set status='CANCELED' where user_id=p_user and status in ('CART','ORDERED');
    -- 배송 개인정보도 익명화하고 결제/상품 스냅샷만 남깁니다.
    update public.orders set recipient='탈퇴 회원', phone='', address='' where user_id=p_user;
    update public.users set email=id::text || '@deleted.invalid', name='탈퇴 회원', phone='', address='',
      password_hash='!disabled', is_active=false, token_version=token_version+1, updated_at=now() where id=p_user;
    return '{}'::jsonb;
  elsif p_action in ('cart_add','cart_set','cart_remove') then
    select * into o from public.orders where user_id=p_user and status='CART' for update;
    if not found then
      if p_action <> 'cart_add' then raise exception 'NOT_FOUND'; end if;
      insert into public.orders(user_id) values (p_user) returning * into o;
    end if;
    v_id=(p_data->>'product_id')::uuid;
    select * into v_product from public.products where id=v_id;
    if not found then raise exception 'NOT_FOUND'; end if;
    if p_action='cart_remove' then
      delete from public.order_items where order_id=o.id and product_id=v_id;
    else
      if not v_product.is_active then raise exception 'PRODUCT_UNAVAILABLE'; end if;
      v_qty=(p_data->>'quantity')::integer;
      if p_action='cart_add' then
        v_qty=v_qty+coalesce((select quantity from public.order_items where order_id=o.id and product_id=v_id),0);
      end if;
      if v_qty not between 1 and 99 then raise exception 'QUANTITY_INVALID'; end if;
      if v_qty > v_product.stock then raise exception 'OUT_OF_STOCK'; end if;
      if not exists(select 1 from public.order_items where order_id=o.id and product_id=v_id)
        and (select count(*) from public.order_items where order_id=o.id)>=50 then raise exception 'CART_LIMIT'; end if;
      insert into public.order_items(order_id,product_id,product_name,unit_price,quantity)
        values(o.id,v_product.id,v_product.name,v_product.price,v_qty)
        on conflict(order_id,product_id) do update set quantity=excluded.quantity,unit_price=excluded.unit_price,product_name=excluded.product_name;
    end if;
    update public.orders set total_amount=coalesce((select sum(unit_price*quantity) from public.order_items where order_id=o.id),0) where id=o.id;
    return public.shop_order_json(o.id);
  elsif p_action='checkout' then
    if p_data->>'source'='cart' then
      select * into o from public.orders where user_id=p_user and status='CART' for update;
      if not found then raise exception 'EMPTY_CART'; end if;
    elsif p_data->>'source'='direct' then
      v_id=(p_data->>'product_id')::uuid;
      v_qty=(p_data->>'quantity')::integer;
      if v_qty not between 1 and 99 then raise exception 'QUANTITY_INVALID'; end if;
      select * into v_product from public.products where id=v_id;
      if not found then raise exception 'NOT_FOUND'; end if;
      -- 별도 ORDERED 행을 만들어 기존 장바구니를 그대로 유지합니다.
      insert into public.orders(user_id,status,total_amount,ordered_at)
        values(p_user,'ORDERED',v_product.price*v_qty,now()) returning * into o;
      insert into public.order_items(order_id,product_id,product_name,unit_price,quantity)
        values(o.id,v_product.id,v_product.name,v_product.price,v_qty);
    else raise exception 'INVALID_REQUEST'; end if;
    if not exists(select 1 from public.order_items where order_id=o.id) then raise exception 'EMPTY_CART'; end if;
    perform 1 from public.products where id in (select product_id from public.order_items where order_id=o.id) order by id for update;
    for it in select i.*, p.stock, p.is_active from public.order_items i join public.products p on p.id=i.product_id where i.order_id=o.id loop
      if not it.is_active then raise exception 'PRODUCT_UNAVAILABLE'; end if;
      if it.quantity>it.stock then raise exception 'OUT_OF_STOCK'; end if;
    end loop;
    update public.order_items i set unit_price=p.price,product_name=p.name from public.products p where i.product_id=p.id and i.order_id=o.id;
    select sum(unit_price*quantity) into v_sum from public.order_items where order_id=o.id;
    if length(coalesce(p_data->>'recipient','')) not between 1 and 60
      or length(coalesce(p_data->>'phone','')) not between 7 and 30
      or length(coalesce(p_data->>'address','')) not between 5 and 300 then raise exception 'SHIPPING_REQUIRED'; end if;
    update public.orders set status='ORDERED',total_amount=v_sum,ordered_at=now(),
      recipient=p_data->>'recipient',phone=p_data->>'phone',address=p_data->>'address' where id=o.id;
    return public.shop_order_json(o.id);
  elsif p_action in ('pay','cancel') then
    select * into o from public.orders where id=(p_data->>'order_id')::uuid and user_id=p_user for update;
    if not found then raise exception 'NOT_FOUND'; end if;
    if p_action='cancel' then
      if o.status <> 'ORDERED' then raise exception 'INVALID_STATUS'; end if;
      update public.orders set status='CANCELED' where id=o.id;
      return public.shop_order_json(o.id);
    end if;
    v_key=(p_data->>'idempotency_key')::uuid;
    select * into v_payment from public.payments where user_id=p_user and idempotency_key=v_key;
    if found and v_payment.order_id<>o.id then raise exception 'KEY_REUSED'; end if;
    if o.status='PAID' then return public.shop_order_json(o.id); end if;
    if o.status<>'ORDERED' then raise exception 'INVALID_STATUS'; end if;
    perform 1 from public.products where id in (select product_id from public.order_items where order_id=o.id) order by id for update;
    for it in select i.*,p.stock,p.is_active from public.order_items i join public.products p on p.id=i.product_id where i.order_id=o.id loop
      if not it.is_active then raise exception 'PRODUCT_UNAVAILABLE'; end if;
      if it.quantity>it.stock then raise exception 'OUT_OF_STOCK'; end if;
    end loop;
    update public.products p set stock=p.stock-i.quantity from public.order_items i where i.product_id=p.id and i.order_id=o.id;
    insert into public.payments(order_id,user_id,amount,idempotency_key) values(o.id,p_user,o.total_amount,v_key);
    update public.orders set status='PAID',paid_at=now() where id=o.id;
    return public.shop_order_json(o.id);
  end if;
  raise exception 'INVALID_REQUEST';
end;
$$;
revoke all on function public.shop_order_json(uuid) from public, anon, authenticated;
revoke all on function public.shop_mutate(uuid,integer,text,jsonb) from public, anon, authenticated;
grant execute on function public.shop_order_json(uuid), public.shop_mutate(uuid,integer,text,jsonb) to service_role;
commit;
