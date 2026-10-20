def test(a,b,c):
    print(a,b,c)

params={'a':1,'b':2,'c':3}
#test(a=1,b=2,c=3)
test(**params)

next_id=1
print({'id':next_id,**params})