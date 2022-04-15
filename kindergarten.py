import pandas as pd

namelist=pd.read_csv('name.csv')
#print(namelist)

f = open('data.txt',encoding='utf-8')   #设置文件对象
data = f.read()     #将txt文件的所有内容读入到字符串str中
f.close()   #将文件关闭
print(str)
x=[]
for name in namelist['name']:
    if data.find(name)==-1:
        x.append(name)
        print(name,'未接龙')
if x==[]:
    print('所有人已接龙')
input("Press <enter>")