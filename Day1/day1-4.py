#print("2 x 1 = 2")
#print("2 x 2 = 4")
#print("2 x 3 = 6")
#print("2 x 4 = 8")

for dan in range(2,10):
    for i in range(1,10):
        print(f"{dan} X {i} = {dan*i}")
    print("================================")

'''
2 x 1 = 2  3 x 1 = 3  4 x 1 = 4
2 x 2 = 4  3 x 2 = 6  4 x 2 = 8
2 x 3 = 6  3 x 3 = 9  4 x 3 = 12
'''

for dan in range(1,5):
    for i in range(2,5):
        print(f"{i} X {dan} = {dan*i}", end="\t")
    print("\n================================")
