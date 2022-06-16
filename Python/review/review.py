import yaml
from time import sleep
import random
import argparse

def readFile():
    global file
    f = open(config)
    file = yaml.safe_load(f.read())

def randomList():
    l1lens = len(dict(file)) - 1
    l1ran = random.randint(0,l1lens)
    l1rans = l1ran
    level1 = list(file)[l1rans]
    print(level1)
    sleep(1)

    l2lens = len(dict(file)[level1]) - 1
    l2ran = random.randint(0,l2lens)
    l2rans = l2ran
    l2 = dict(file)[level1]
    level2 = list(l2)[l2rans]
    print('   - ' + level2)
    sleep(1)
    
    try:
        l3lens = len(dict(file)[level1][level2]) - 1 
        l3ran = random.randint(0,l3lens)
        l3rans = l3ran
        l3 = dict(file)[level1][level2]
        level3 = list(l3)[l3rans]
        print('      - ' + str(level3))
        sleep(1)
    except:
        pass

    try:
        l4lens = len(dict(file)[level1][level2][level3]) - 1
        l4ran = random.randint(0,l4lens)
        l4rans = l4ran
        l4 = dict(file)[level1][level2][level3]
        level4 = list(l4)[l4rans]
        print('         - ' + str(level4))
        sleep(1)
    except:
        pass

    try:
        l5lens = len(dict(file)[level1][level2][level3][level4]) - 1
        l5ran = random.randint(0,l5lens)
        l5rans = l5ran
        l5 = dict(file)[level1][level2][level3][level4]
        level5 = list(l5)[l5rans]
        print('            - ' + str(level5))
        sleep(1)
    except:
        pass

def randrun():
    l1lens = len(dict(file))
    inf = '\n========================================================\n'
    if l1lens > 3:
        randnums = l1lens / 3 + 3

        randnums1 = int(randnums)
        randnum = random.randint(randnums1, randnums1 + 2)

        print("%s当前有 %d 个知识版块,随机抽取 %d 次%s" % (inf, l1lens, randnum, inf))
        for i in range(0, randnum):
            print('\n第 %s 次抽取：' % (i + 1))
            randomList()

    else :
        l1lens = len(dict(file))
        print("%s共有 %d 知识个版块,随机抽取 3 次%s" % (inf, l1lens, inf))
        for i in range(3):
            print('\n第 %s 次抽取：' % (i + 1))
            randomList()

#randomList()
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = '这个脚本是用来随机抽取要复习的部分')
    parser.add_argument("--config", default = "config.yaml", help = '这个参数是你的配置文件，必需是yaml格式的')
    args = parser.parse_args()
    config = args.config

    readFile()
    randrun()
