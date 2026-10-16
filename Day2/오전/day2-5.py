#포함관계(in, not in)
role = 'admin'

# if role == 'admin' or role == 'manager' or role =='staff'

# allowed_roles= ['admin', 'manager','staff']
if role in ['admin', 'manager','staff']:
    print('접근 허용')
else:
    print('접근 불가')