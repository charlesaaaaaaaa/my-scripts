from poplib import POP3
from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr


#################################邮箱信息###########################
email = "2488347738@qq.com"
password = "pulrwhxdjkcodjhi"
pop3_server = "pop.qq.com"
server = POP3(pop3_server)                        #连接到POP3服务器

################################邮箱解析############################
value = ['','','']
def printMsg(msg):
	global value 
	i = 0
	for header in ['From', 'To', 'Subject']:      #解析邮件头
		value[i] = msg.get(header, '')
		if value[i]:
			if header == 'Subject':                 #解析主题
				value[i] = decode_str(value[i])
			else:
				hdr, addr = parseaddr(value[i])
				name = decode_str(hdr)
				value[i] = u'%s <%s>' % (name, addr)
		i = i+1

def decode_str(s):
	value, charset = decode_header(s)[0]
	if charset:
		value = value.decode(charset)
	return value
####################################################################
#server.set_debuglevel(1)                                #开闭调试信息
#print (server.getwelcome().decode('utf-8'))              #打印欢迎信息
server.user(email)                                       #身份认证邮箱地址
server.pass_(password)                                   #身份认证,邮箱密码

emailNum, size = server.stat()
print ("Messages: %s. size: %s" % (emailNum, size))      #返回邮箱的数量和占用空间
resp, mails, octets = server.list()                      #返回所有邮箱的编号  
index = len(mails)                                       #获取最新的一封邮件, 索引从1开始

resp, lines, octets = server.top(index,0)                #只获取邮箱的头

msg_content = b'\r\n'.join(lines).decode('utf-8')        #每一行加入换行,并转化为UTF-8类型
msg = Parser().parsestr(msg_content)                     #把邮件内容解析成Message对象

printMsg(msg)
print (value)

#server.dele(index)                                      #可以根据索引号从服务器删除邮件
server.quit()                                            #关闭连接

