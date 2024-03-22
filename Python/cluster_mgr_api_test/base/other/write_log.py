import time

class w2File():
    def __init__(self):
        today = time.strftime("%Y-%m-%d")
        log_name = "%s.log" % today
        self.log_location = './log/%s' % log_name

    def tolog(self, txt):
        log_location = self.log_location
        now_time = time.ctime()
        with open(log_location, 'a', encoding='utf-8') as f:
            f.write('%s %s\n' % (now_time, txt))
        f.close()

    def toOther(self, file_name, txt):
        with open(file_name, 'a', encoding='utf-8') as f:
            f.write(txt)
        f.close()
