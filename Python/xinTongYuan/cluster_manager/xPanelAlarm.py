# -*- coding: utf-8 -*-
import re
import linecache
import time
from selenium import webdriver
from time import sleep
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options #使用无头浏览器
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.keys import Keys
import argparse
import subprocess
from selenium.webdriver.common.action_chains import ActionChains

def start(host, port):  # 开启driver
    global driver
    options = ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    
    '''
    # 这里被注释的是windows的部分
    # driver = webdriver.Chrome(executable_path='D:\python3\chromedriver.exe')
    # driver = webdriver.Chrome()
    s = Service("D:\python3\chromedriver.exe")
    driver = webdriver.Chrome(service=s)
    '''
    #这部分是linux的
    s=Service('./chromedriver')

    ch_options = Options()
    #ch_options.add_argument("--headless")
    ch_options.add_argument('--no-sandbox')
    ch_options.add_argument('--disable-gpu')
    ch_options.add_argument('--disable-dev-shm-usage')
    #driver = webdriver.Chrome(options=ch_options)
    driver = webdriver.Chrome()
    driver.implicitly_wait(5)
    urls = 'http://%s:%d/KunlunXPanel' % (host, port)
    print(urls)
    driver.get(urls)
    return driver

def load_xpanel():
    sleep(3)
    load_startTime = time.time()
    driver.find_element(By.NAME, "username").send_keys('super_dba')
    driver.find_element(By.NAME, 'password').send_keys('Qwer1234.')
    driver.find_element(By.XPATH, '//*[@id="app"]/div/div/form/button/span').click()
    sleep(1)
    load_endTime = time.time()
    print('\r登录中 完成     ')
    print('本次登录使用了 %.2f 秒' % (load_endTime - load_startTime))

def test():
    global atti_type, storage_host, storage_port
    print('========\n开始操作xPanel...')
    atti_type = '存储节点异常'
    sleep(1)
    #检查有几个shard几个副本
    driver.find_element(By.XPATH, '/html/body/div/div/div[2]/section/div/div/div[2]/div[1]/div/div[2]/div[4]/div[2]/table/tbody/tr/td[7]/div/button[4]/span').click()
    numTxt = driver.find_element(By.XPATH, '/html/body/div/div/div[2]/section/div/div/div[2]/div[4]/div/div[2]/div/form/div[5]/div/span').text
    numTxt_total = re.findall('0|[1-9]', numTxt)
    shard_num = int(numTxt_total[0])
    replica_nums = int(numTxt_total[2])
    print('该集群有%s个shard，每个shard有%s个副本' % (shard_num, replica_nums))
    driver.find_element(By.XPATH, '/html/body/div/div/div[2]/section/div/div/div[2]/div[4]/div/div[1]/div/ul/li[9]/span').click()

    #选择一个主用来触发告警的存储节点
    num = 1
    while num <= replica_nums + 1:
        role = driver.find_element(By.XPATH, '/html/body/div/div/div[2]/section/div/div/div[2]/div[4]/div/div[2]/div/div[2]/div[3]/table/tbody/tr[2]/td/div/div[3]/table/tbody/tr[%s]/td[5]/div/span' % (num)).text
        if role == '主':
            storage_host = driver.find_element(By.XPATH, '/html/body/div/div/div[2]/section/div/div/div[2]/div[4]/div/div[2]/div/div[2]/div[3]/table/tbody/tr[2]/td/div/div[3]/table/tbody/tr[%s]/td[2]/div' % (num)).text
            storage_port = driver.find_element(By.XPATH, '/html/body/div/div/div[2]/section/div/div/div[2]/div[4]/div/div[2]/div/div[2]/div[3]/table/tbody/tr[2]/td/div/div[3]/table/tbody/tr[%s]/td[3]/div' % (num)).text
            break
        num = num + 1
    print('选择其中一个存储分片主节点：%s:%s'% ( storage_host, storage_port))

    #设置用户信息，先进入 系统管理
    driver.find_element(By.XPATH,'/html/body/div/div/div[1]/div/div[1]/div/ul/div[7]/li/div/span').click()
    driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div/div[1]/div/ul/div[7]/li/ul/div[1]/a/li/span').click() #点击用户管理
    sleep(1)
    #开始检查是否存在test这个用户，如果有就点击删除按钮, 先获取用户总个数
    cNum = driver.find_element(By.XPATH,'/html/body/div[1]/div/div[2]/section/div/div[3]/div/span[1]').get_attribute('innerHTML')
    cTotalNum = re.findall('0|[1-99]', cNum)
    iTotalNum = int(cTotalNum[0])
    try:
        for i in range(iTotalNum):
            i = i + 1
            userName = driver.find_element(By.XPATH,'/html/body/div[1]/div/div[2]/section/div/div[2]/div[3]/table/tbody/tr[%s]/td[2]/div/span' % (i)).get_attribute('innerHTML')
            if userName == 'test':
                sleep(5)
                #点击删除按键
                driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/section/div/div[2]/div[3]/table/tbody/tr[%s]/td[7]/div/button[2]/span' % (i)).click()
                #点击确定
                driver.find_element(By.XPATH, '/html/body/div[2]/div/div[3]/button[2]/span').click()
                print('删除旧test用户成功，新增新test用户。。。')
    except:
        pass
    # 开始新增test用户, 点击新增
    driver.find_element(By.XPATH, '/html/body/div/div/div[2]/section/div/div[1]/div/button[3]/span').click()
    num = 0
    for i in 'test', 'Qwer1234.', 'Qwer1234.', '12345678911', '2488347738@qq.com':
        num = num + 1
        driver.find_element(By.XPATH,
                            '/html/body/div[1]/div/div[2]/section/div/div[4]/div/div[2]/form/div[%i]/div/div[1]/input' % (num)).send_keys(i)
    sleep(1)
    #重新获取一次用户总数
    driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/section/div/div[4]/div/div[3]/div/button[2]/span').click()
    cNum = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/section/div/div[3]/div/span[1]').get_attribute(
        'innerHTML')
    cTotalNum = re.findall('0|[1-99]', cNum)
    iTotalNum = int(cTotalNum[0])

    #开始新增告警, 点击告警终端管理
    print('开始新增告警 -- 存储节点异常')
    driver.find_element(By.XPATH, '/html/body/div/div/div[1]/div/div[1]/div/ul/div[2]/a/li').click()
    driver.find_element(By.XPATH, '/html/body/div/div/div[2]/section/div/div[3]/div[1]/button[4]/span').click()
    #开始查找接受处理人为空（因为上一步删除了test用户，故如果之前存在test的告警应该在用户处为空）且告警类型为存储节点异常的告警并删除，无则不做任何事
    try:
        cru_alarm_types = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/section/div/div[2]/div/div/section/div/div[2]/div[1]/div/div[3]/table/tbody/tr/td[1]/div/span').text
        print(cru_alarm_types, atti_type)
        num = 1
        while cru_alarm_types != atti_type:
            cru_alarm_types = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/section/div/div[2]/div/div/section/div/div[2]/div[1]/div/div[3]/table/tbody/tr[%s]/td[1]/div/span' % (num)).text
            print(cru_alarm_types, atti_type)
            num = num + 1
        print(num)
        if num == 1:
            button_del = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/section/div/div[2]/div/div/section/div/div[2]/div[1]/div/div[3]/table/tbody/tr/td[5]/div/button[2]/span')
            driver.execute_script("arguments[0].click();",button_del)
        else:
            button_del = driver.find_element(By.XPATH,
                                '/html/body/div[1]/div/div[2]/section/div/div[2]/div/div/section/div/div[2]/div[1]/div/div[3]/table/tbody/tr[%s]/td[5]/div/button[2]/span' % (
                                    num - 1))
            driver.execute_script("arguments[0].click();", button_del)
        errCode = driver.find_element(By.XPATH, '/html/body/div[2]/div/div[2]/div[1]/div[2]/p').text
        errCode = re.findall('0|[0-9][0-9][0-9][0-9]', errCode)
        print(errCode)
        errCode = errCode[0]
        print(errCode)
        driver.find_element(By.XPATH, '/html/body/div[2]/div/div[2]/div[2]/div[1]/input').send_keys(errCode)
        driver.find_element(By.XPATH, '/html/body/div[2]/div/div[3]/button[2]/span').click()
    except Exception as a:
        print('当前没有旧的告警管理配置')
        #print(a)
    driver.find_element(By.XPATH,
                            '/html/body/div[1]/div/div[2]/section/div/div[2]/div/div/header/button/i').click()  # 点击关闭
    #点击新增
    driver.find_element(By.XPATH, '/html/body/div/div/div[2]/section/div/div[3]/div[1]/button[3]/span').click()
    #点击告警类型
    sleep(1)
    driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/section/div/div[1]/div/div[2]/form/div[1]/div/div/div/input').click()
    #开始逐个查找类型为 存储节点异常 的选择
    for i in range(1, 17):
        for j in range(3, 6):
            print(j)
            try:
                alType = driver.find_element(By.XPATH, '/html/body/div[%s]/div[1]/div[1]/ul/li[%s]/span' % (j, i))
                alTypeTxt = alType.text
                if alTypeTxt == atti_type:
                    alType.click()
                    break
            except:
                pass
        if alTypeTxt == atti_type:
            break
        else:
            print(i)

    #逐个查找test用户
    driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/section/div/div[1]/div/div[2]/form/div[2]/div/div/div/input').click()
    for i in range(1, iTotalNum + 1):
        sleep(1)
        findEls = 0
        a = j + 1
        while findEls == 0:
            try:
                sleUser = driver.find_element(By.XPATH, '/html/body/div[%s]/div[1]/div[1]/ul/li[%s]/span' % (a, i))
                sleUserTxt = sleUser.text
                findEls == 1
                print(sleUserTxt)
                break
            except:
                findEls == 0
                print(a)
                a = a + 1
        if sleUserTxt == 'test':
            sleUser.click()
            break
    if sleUserTxt != 'test':
        print('未找到test用户')
        exit(1)
    # 是否生效，是
    sleep(1)
    j = a + 1
    driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/section/div/div[1]/div/div[2]/form/div[4]/div/div/div/input').click()
    driver.find_element(By.XPATH, '/html/body/div[%s]/div[1]/div[1]/ul/li[1]/span' % (j)).click()
    #提醒方式, 邮件
    sleep(1)
    a = j + 1
    driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/section/div/div[1]/div/div[2]/form/div[3]/div/div/div[2]/input').click()
    driver.find_element(By.XPATH, '/html/body/div[%s]/div[1]/div[1]/ul/li[3]/span' % (a)).click()
    sleep(1)
    #点击确定
    driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/section/div/div[1]/div/div[3]/div/button[2]/span').click()

    #增加告警发送邮箱 -- 告警管理 -- 配置管理 -- 阿里云邮箱 -- 配置key和邮箱
    print('开始配置发件邮箱信息')
    driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/section/div/div[3]/div[1]/button[4]/span').click()
    sleep(1)
    driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/section/div/div[2]/div/div/section/div/div[1]/div/div/div/div[3]').click()
    driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/section/div/div[2]/div/div/section/div/div[2]/div[2]/div/div[1]/div/div/div/div[3]').click()
    AccessKeyId = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/section/div/div[2]/div/div/section/div/div[2]/div[2]/div/div[2]/div[2]/form/div[1]/div/div/input')
    AccessKeyId.clear()
    AccessKeyId.send_keys(AccessKeyId1)
    SecretKey = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/section/div/div[2]/div/div/section/div/div[2]/div[2]/div/div[2]/div[2]/form/div[2]/div/div/input')
    SecretKey.clear()
    SecretKey.send_keys(SecretKey1)
    sendEMail = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/section/div/div[2]/div/div/section/div/div[2]/div[2]/div/div[2]/div[2]/form/div[3]/div/div/input')
    sendEMail.clear()
    sendEMail.send_keys(Email1)
    sleep(1)
    #点击保存
    driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/section/div/div[2]/div/div/section/div/div[2]/div[2]/div/div[2]/div[2]/form/div[4]/div/button/span').click()
    driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/section/div/div[2]/div/div/header/button/i').click()

    #去选中的服务器进行进行不间断kill掉对应的存储节点进程
    print('开始不间断kill掉对应的存储节点进程一段时间，使其触发存储节点异常告警')
    killStorageProcess = "ssh %s@%s \"ps -ef | grep %s | awk '{print \\$2}' | xargs kill -9\" > /dev/null 2>&1" % (User, storage_host, storage_port)
    print(killStorageProcess)
    start_time = time.time()
    for i in range(500):
        subprocess.run(killStorageProcess, shell=True)
    end_time = time.time()
    print(end_time - start_time)

    sleep(30)
    #开始检查是否存在’存储节点异常‘, 告警终端管理 -- 逐个检查是否存在存储节点异常
    driver.refresh()
    driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/section/div/div[5]/div/span[2]/div/div/span/span/i').click()#点击页数下拉框
    driver.find_element(By.XPATH, '/html/body/div[2]/div[1]/div[1]/ul/li[4]/span').click()#点击50条/页
    driver.find_element(By.XPATH, '/html/body/div/div/div[1]/div/div[1]/div/ul/div[2]/a/li/span').click()
    alarm_num = driver.find_element(By.XPATH, '/html/body/div/div/div[2]/section/div/div[5]/div/span[1]').text
    alarm_Total_num = re.findall('\d+', alarm_num)
    print(alarm_Total_num)
    alarm_Total_num = int(alarm_Total_num[0])
    i = 1
    a = 0
    while i <= alarm_Total_num:
        alarm_Type = driver.find_element(By.XPATH, '/html/body/div/div/div[2]/section/div/div[4]/div[3]/table/tbody/tr[%s]/td[2]/div/span' % (i)).text
        try:
            assert alarm_Type == '存储节点异常'
            alarm_object = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/section/div/div[4]/div[3]/table/tbody/tr[%s]/td[3]/div' % (i)).text
            alarm_split = alarm_object.split('_')
            alarm_host = alarm_split[0]
            alarm_port = alarm_split[1]
            print(i, alarm_Type, alarm_split, alarm_host, alarm_port)
            if alarm_port == storage_port and alarm_host == storage_host:
                print('当前指定存储节点已触发异常告警，进行下一步操作')
                a = 1
                break
            print(alarm_Type)
        except:
            print('%s: %s' % (i,alarm_Type))
        i = i + 1
    if a != 1:
        print('未找到对应的异常情况，失败')
        exit(1)

    subprocess.run('python3 getEmail.py %s > tmp.txt' % (atti_type), shell=True)

def check_email():
    print('========\n检查邮件。。。')
#查看邮件标题是啥
    lines = linecache.getline('tmp.txt', 5)
    attitus = lines.split(' ')[1].split('s')[0]
    if attitus == atti_type:
        print('========\n查找到当前邮件为 %s 告警\n进行下一步检查...' % (atti_type))
    else:
        exit(1)

#查看对应的内容
    lines = linecache.getline('tmp.txt', 11)
    linesplit = lines.split(',')
#查找host、port
    cStorage_host = linesplit[4].split(':')[1].replace('"', '')
    cStorage_port = linesplit[5].split(':')[1].split('}')[0].replace('"', '')
    print('当前邮件提及的节点为: %s:%s'% (cStorage_host, cStorage_port))

#检查是否为正确的host和port
    print('========')
    if cStorage_host == storage_host:
        if cStorage_port == storage_port:
            print("检查正确，通过, 邮件信息如下：")
            subprocess.run('cat tmp.txt', shell = True)
        else:
            print("port不正确，失败")
    else:
        print('host不正确，失败')
    subprocess.run('rm tmp.txt', shell = True)


if __name__ == '__main__':
    ps = argparse.ArgumentParser(description='install KunlunBase cluster with Xpanel')
    ps.add_argument('--host', help="Xpanel host", default='192.168.0.125', type=str)
    ps.add_argument('--port', help='Xpanel port', default=18851, type=int)
    ps.add_argument('--user', help="所有涉及到的服务器的通用用户，必须要有ssh互信免密权限",default='kunlun', type=str)
    ps.add_argument('--AccessKeyId', help="阿里云email的AccessKeyId", type=str)
    ps.add_argument('--AccessKeySecret', help="阿里云email的AccessKeySecret", type=str)
    ps.add_argument('--Email', help="阿里云email账号", type=str)
    args = ps.parse_args()
    Host = args.host
    Port = args.port
    User = args.user
    AccessKeyId1 = args.AccessKeyId
    SecretKey1 = args.SecretKey
    Email1 = args.Email
    print(args)
    start(Host, Port)
    load_xpanel()
    test()
    check_email()
