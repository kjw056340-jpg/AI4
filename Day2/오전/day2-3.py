class SafeProfile:
    def __init__(self):
        pass
    def get(self,key):
        return True
    def set(self,key):
        return True

user_profile = SafeProfile()
#user_profile=None
print(user_profile.get('is_verified'))
if user_profile and user_profile.get('is_verified'):
    print('성공')
else:
    print('실패')