import random
import time


def randdate():
    year = random.randint(1970, 2023)
    month = random.randint(1, 12)
    bigMonth = (1, 3, 5, 7, 8, 10, 12)
    smallMonth = (4, 6, 9, 11)
    if year % 4 == 0 and year % 400 != 0:
        if month == 2:
            day = random.randint(1, 29)
        elif month in bigMonth:
            day = random.randint(1, 31)
        elif month in smallMonth:
            day = random.randint(1, 30)
    else:
        if month == 2:
            day = random.randint(1, 28)
        elif month in bigMonth:
            day = random.randint(1, 31)
        elif month in smallMonth:
            day = random.randint(1, 30)
    if month < 10:
        month = '0' + str(month)
    if day < 10:
        day = '0' + str(day)
    randate = '%s-%s-%s' % (year, month, day)
    return randate

def randstr(per):
    res = ''
    for i in range(per):
        a = random.choice('abcdefghijklmnopqrstuvwxyzQWERTYUIOPASDFGHJKLZXCVBNM1234567890')
        res = res + a
    return res

def randtime():
    hours = random.randint(0, 23)
    if hours < 10:
        hours = '0' + str(hours)
    mins = random.randint(0, 59)
    if mins < 10:
        mins = '0' + str(mins)
    seconds = random.randint(0, 59)
    if seconds < 10:
        seconds = '0' + str(seconds)
    ns = random.randint(0, 999)
    times = '%s:%s:%s.%s' % (hours, mins, seconds, ns)
    return times

def randtimez():
    timez = ["NZDT", "NZST", "NZT", "AESST", "CST", "CADT", "SADT", "EST", "LIGT", "CAST", "WDT", "JST", "KST", "CCT",
             "EETDST", "CETDST", "EET", "IST", "MEST", "METDST", "BST", "CET", "MET", "WETDST", "GMT", "WET", "WAT",
             "NDT", "ADT", "NFT", "NST", "AST", "EDT", "CDT", "EST", "CST", "MDT", "MST", "PDT", "PST"]
    times = randtime()
    randTimez = random.choice(timez)
    timez = '%s %s' % (times, randTimez)
    return timez

def randtimestamp():
    dates = randdate()
    times = randtime()
    randts = dates + ' ' + times
    return randts

def randtimestampz():
    dates = randdate()
    zones = randtimez()
    timestampz = dates + ' ' + zones
    return timestampz

def randMac():
    res = ":".join(["%02x" % x for x in map(lambda x: random.randint(0, 255), range(6))])
    return res

def randnet():
    resList = []
    for i in range(4):
        parts = str(random.randint(0,255))
        resList.append(parts)
    res = '.'.join(resList)
    return res

def randbit(per):
    res = ''
    for i in range(per):
        tmp = random.randint(0, 1)
        res = res + str(tmp)
    return res

def timer(func):
    def wapper(*args, **kwargs):
        startTime = time.time()
        res = func(*args, **kwargs)
        endTime = time.time()
        spendTime = endTime - startTime
        print(f'运行时间 {func.__name__}: {spendTime} 秒')
        return res
    return wapper