-- Apply AFTER 001, 002, 003. Back up the DB first; test on a separate Supabase project.
-- Existing shop user UUIDs/orders remain unchanged. Legacy users need explicit Auth linking.
-- Repeatable: existing columns are preserved; functions/triggers are refreshed.
begin;
alter table public.users add column if not exists auth_user_id uuid unique references auth.users(id) on delete restrict;
alter table public.users add column if not exists role text not null default 'member' check (role in ('member','admin'));
alter table public.users alter column password_hash drop not null;
-- Hashes are no longer used by the application. Erase them after Auth migration verification,
-- using the documented cleanup command, so a backup remains available during migration.

create or replace function public.shop_auth_profile() returns trigger
language plpgsql security definer set search_path = '' as $$
begin
  -- Never link legacy records solely on an unverified signup email.
  -- A trusted operator explicitly links existing users after identity verification.
  if exists(select 1 from public.users where email=lower(new.email)) then
    return new;
  end if;
  insert into public.users(auth_user_id,email,name,phone,address)
  values(new.id,lower(new.email),
    left(coalesce(nullif(trim(new.raw_user_meta_data->>'name'),''),'회원'),60),
    left(coalesce(new.raw_user_meta_data->>'phone',''),30),
    left(coalesce(new.raw_user_meta_data->>'address',''),300));
  return new;
end;
$$;
revoke all on function public.shop_auth_profile() from public, anon, authenticated;
create or replace trigger shop_auth_profile_insert after insert on auth.users
for each row execute function public.shop_auth_profile();

-- No browser access to private profiles/orders/payments or transaction RPCs.
-- The backend uses a server-only key, authenticates via /auth/v1/user and checks
-- ownership and the current private role. Do not grant authenticated direct writes.
alter table public.users enable row level security;
alter table public.products enable row level security;
alter table public.orders enable row level security;
alter table public.order_items enable row level security;
alter table public.payments enable row level security;
revoke all on public.users, public.products, public.orders, public.order_items, public.payments from anon, authenticated;

create or replace function public.shop_mutate(p_user uuid, p_version integer, p_action text, p_data jsonb default '{}')
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
      updated_at=now() where id=p_user returning * into u;
    return to_jsonb(u) - 'password_hash';
  elsif p_action='delete_account' then
    update public.orders set status='CANCELED' where user_id=p_user and status in ('CART','ORDERED');
    -- 배송 개인정보도 익명화하고 결제/상품 스냅샷만 남깁니다.
    update public.orders set recipient='탈퇴 회원', phone='', address='' where user_id=p_user;
    update public.users set email=id::text || '@deleted.invalid', name='탈퇴 회원', phone='', address='',
      password_hash=null, is_active=false, token_version=token_version+1, updated_at=now() where id=p_user;
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

revoke all on function public.shop_mutate(uuid,integer,text,jsonb) from public, anon, authenticated;
grant execute on function public.shop_mutate(uuid,integer,text,jsonb) to service_role;

-- Refresh the Data API schema after the transaction commits.
notify pgrst, 'reload schema';
commit;
