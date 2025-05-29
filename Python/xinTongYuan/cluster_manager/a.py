with open('a.txt', 'r') as f:
    msg = f.read()
#print(msg)
head = msg.split('--------------------')[0]
txt = msg.split('--------------------')[1].split(':')[1]
a = head.split(':')[-1].split('part')[0]
print(a)
print(txt)
