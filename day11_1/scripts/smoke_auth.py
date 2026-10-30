"""Check Supabase Auth through the local app using existing confirmed TEST accounts."""
import argparse
from getpass import getpass
from urllib.parse import urlsplit
from uuid import uuid4

import httpx


def expect(response, status, label):
    if response.status_code != status:
        raise RuntimeError(f'{label}: expected {status}, received {response.status_code}')
    print(f'PASS {label}')
    return response


def login(base, email, password):
    client = httpx.Client(base_url=base, timeout=30)
    try:
        csrf = expect(client.get('/api/csrf'), 200, 'CSRF').json()['csrf_token']
        client.headers.update({'Origin': base, 'X-CSRF-Token': csrf})
        response = expect(client.post('/api/auth/login', json={'email': email, 'password': password}), 200, 'login')
        return client, response.json()['user']
    except Exception:
        client.close()
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', default='http://127.0.0.1:8000')
    parser.add_argument('--member-email', required=True)
    parser.add_argument('--other-email', required=True)
    parser.add_argument('--admin-email')
    args = parser.parse_args()
    base = args.base_url.rstrip('/')
    url = urlsplit(base)
    if url.scheme != 'http' or url.hostname not in {'localhost', '127.0.0.1'} or url.path or url.username:
        parser.error('Use a local http://127.0.0.1 or http://localhost app URL.')
    passwords = [getpass('Member password: '), getpass('Other member password: ')]
    if args.admin_email:
        passwords.append(getpass('Admin password: '))
    clients = []
    try:
        with httpx.Client(base_url=base, timeout=30) as guest:
            expect(guest.get('/health'), 200, 'health')
            expect(guest.get('/api/products'), 200, 'public catalog')
            expect(guest.get('/api/me'), 401, 'guest denied')
        member, user = login(base, args.member_email, passwords[0])
        clients.append(member)
        other, other_user = login(base, args.other_email, passwords[1])
        clients.append(other)
        if user['id'] == other_user['id'] or user['role'] != 'member' or other_user['role'] != 'member':
            raise RuntimeError('Use two different member accounts.')
        expect(member.get('/api/cart'), 200, 'own cart')
        expect(member.get('/api/admin/orders'), 403, 'member denied admin orders')
        expect(member.patch('/api/me', json={'name': user['name'], 'role': 'admin'}), 422, 'role injection denied')
        orders = expect(other.get('/api/orders'), 200, 'other member orders').json()['items']
        if not orders:
            raise RuntimeError('Create an order for the other member in the browser, then rerun.')
        target = orders[0]
        expect(member.get('/api/orders/'+target['id']), 404, 'foreign order read denied')
        expect(member.post('/api/orders/'+target['id']+'/cancel'), 404, 'foreign order cancellation denied')
        expect(member.post('/api/payments', json={'order_id': target['id'], 'idempotency_key': str(uuid4())}),
               404, 'foreign order payment denied')
        payment = target.get('payment')
        if isinstance(payment, list):
            payment = payment[0] if payment else None
        if payment:
            expect(member.get('/api/payments/'+payment['id']), 404, 'foreign payment read denied')
        else:
            print('SKIP foreign payment read: other member has no payment on the latest order')
        expect(member.post('/api/auth/refresh'), 200, 'refresh session')
        saved = dict(member.cookies)
        expect(member.post('/api/auth/logout'), 200, 'logout (all member sessions)')
        member.cookies.clear()
        member.cookies.update(saved)
        expect(member.get('/api/me'), 401, 'old cookies denied after logout')
        expect(member.post('/api/auth/refresh'), 401, 'old refresh denied after logout')
        if args.admin_email:
            admin, admin_user = login(base, args.admin_email, passwords[2])
            clients.append(admin)
            if admin_user['role'] != 'admin':
                raise RuntimeError('The administrator account has no admin role.')
            expect(admin.get('/api/admin/orders'), 200, 'admin orders allowed')
            expect(admin.get('/admin'), 200, 'admin screen allowed')
            expect(admin.post('/api/auth/logout'), 200, 'admin logout')
        expect(other.post('/api/auth/logout'), 200, 'other member logout')
    finally:
        for client in clients:
            client.close()


if __name__ == '__main__':
    main()
