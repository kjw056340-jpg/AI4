-- Run in Supabase SQL Editor AFTER 004_supabase_auth.sql.
-- Trusted operator migration: link only accounts whose email Supabase has verified.
-- Existing shop UUIDs, orders and roles are preserved. Repeatable.
begin;

-- Link legacy shop members to an Auth account that owns the same verified email.
-- Unverified, anonymous, deleted and inactive accounts are never linked.
update public.users u
set auth_user_id=a.id, token_version=u.token_version+1, updated_at=now()
from auth.users a
where u.auth_user_id is null and u.is_active
  and u.email=lower(a.email)
  and a.email_confirmed_at is not null
  and a.deleted_at is null
  and coalesce(a.is_anonymous,false)=false
  and not exists(select 1 from public.users linked where linked.auth_user_id=a.id);

-- Auth signup may have happened before the profile trigger was installed.
-- Create only missing profiles for verified emails; never reactivate former members.
insert into public.users(auth_user_id,email,name,phone,address)
select a.id,lower(a.email),
  left(coalesce(nullif(trim(a.raw_user_meta_data->>'name'),''),'회원'),60),
  left(coalesce(a.raw_user_meta_data->>'phone',''),30),
  left(coalesce(a.raw_user_meta_data->>'address',''),300)
from auth.users a
where a.email is not null and a.email_confirmed_at is not null
  and a.deleted_at is null and coalesce(a.is_anonymous,false)=false
  and not exists(select 1 from public.users u where u.auth_user_id=a.id or u.email=lower(a.email));

commit;

-- Counts only; no passwords or tokens are displayed.
select count(*) as linked_active_members
from public.users where auth_user_id is not null and is_active;
