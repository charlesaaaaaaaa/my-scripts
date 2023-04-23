import re
import sys
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
from multiprocessing import Process
from selenium.webdriver.common.action_chains import ActionChains

def start(host, port):  # 开启driver
    global driver
    options = ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)

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
    '''
    driver.implicitly_wait(180)
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
    sleep(1)
    #选择一个用来触发告警的存储节点
    storage_host = driver.find_element(By.XPATH, '/html/body/div/div/div[2]/section/div/div/div[2]/div[1]/div/div[2]/div[3]/table/tbody/tr/td[6]/div/div/div[3]/table/tbody/tr[1]/td[2]/div').text
    storage_port = driver.find_element(By.XPATH, '/html/body/div/div/div[2]/section/div/div/div[2]/div[1]/div/div[2]/div[3]/table/tbody/tr/td[6]/div/div/div[3]/table/tbody/tr[1]/td[3]/div').text
    print('选择其中一个存储节点：%s:%s'% ( storage_host, storage_port))

    #设置用户信息，先进入 系统管理
    driver.find_element(By.XPATH,'/html/body/div/div/div[1]/div/div[1]/div/ul/div[7]/li/div/span').click()
    driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div/div[1]/div/ul/div[7]/li/ul/div[1]/a/li/span').click() #点击用户管理
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
    for i in 'test', 'Qwer1234.', 'Qwer1234.', '12345678911', 'charles@zettadb.com':
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
    driver.find_element(By.XPATH, '/html/body/div/div/div[1]/div/div[1]/div/ul/div[2]/a/li').click()
    #点击新增
    driver.find_element(By.XPATH, '/html/body/div/div/div[2]/section/div/div[3]/div[1]/button[3]/span').click()
    #点击告警类型
    sleep(1)
    driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/section/div/div[1]/div/div[2]/form/div[1]/div/div/div/input').click()
    #开始逐个查找类型为 存储节点异常 的选择
    for i in range(1, 17):
        alType = driver.find_element(By.XPATH, '/html/body/div[4]/div[1]/div[1]/ul/li[%s]/span' % (i))
        alTypeTxt = alType.text
        if alTypeTxt == '存储节点异常':
            alType.click()
    #逐个查找test用户
    sleep(1)
    driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/section/div/div[1]/div/div[2]/form/div[2]/div/div/div/input').click()
    for i in range(1, iTotalNum + 1):
        sleUser = driver.find_element(By.XPATH, '/html/body/div[5]/div[1]/div[1]/ul/li[%s]/span' % (i))
        sleUserTxt = sleUser.get_attribute('innerHTML')
        if sleUserTxt == 'test':
            sleUser.click()
    # 是否生效，是
    sleep(1)
    driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/section/div/div[1]/div/div[2]/form/div[4]/div/div/div/input').click()
    driver.find_element(By.XPATH, '/html/body/div[6]/div[1]/div[1]/ul/li[1]/span').click()
    #提醒方式, 邮件
    sleep(1)
    driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/section/div/div[1]/div/div[2]/form/div[3]/div/div/div[2]/input').click()
    driver.find_element(By.XPATH, '/html/body/div[7]/div[1]/div[1]/ul/li[3]/span').click()
    sleep(1)
    #点击确定
    driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/section/div/div[1]/div/div[3]/div/button[2]/span').click()

    #增加告警发送邮箱 -- 告警管理 -- 配置管理 -- 阿里云邮箱 -- 配置key和邮箱
    driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/section/div/div[3]/div[1]/button[4]/span').click()
    sleep(1)
    driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/section/div/div[2]/div/div/section/div/div[1]/div/div/div/div[3]').click()
    driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/section/div/div[2]/div/div/section/div/div[2]/div[2]/div/div[1]/div/div/div/div[3]').click()
    AccessKeyId = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/section/div/div[2]/div/div/section/div/div[2]/div[2]/div/div[2]/div[2]/form/div[1]/div/div/input')
    AccessKeyId.clear()
    AccessKeyId.send_keys('LTAI5tJeKKXuWUzYvY3ULKzr')
    SecretKey = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/section/div/div[2]/div/div/section/div/div[2]/div[2]/div/div[2]/div[2]/form/div[2]/div/div/input')
    SecretKey.clear()
    SecretKey.send_keys('JY32MeZR6HSe0USpaSSnh2dEAAiLd2')
    sendEMail = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/section/div/div[2]/div/div/section/div/div[2]/div[2]/div/div[2]/div[2]/form/div[3]/div/div/input')
    sendEMail.clear()
    sendEMail.send_keys('admin@pushmail.kunlunbase.com')
    sleep(1)
    #点击保存
    driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/section/div/div[2]/div/div/section/div/div[2]/div[2]/div/div[2]/div[2]/form/div[4]/div/button/span').click()
    driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/section/div/div[2]/div/div/header/button/i').click()

    #去选中的服务器进行进行不间断kill掉对应的存储节点进程
    killStorageProcess = "ssh %s@%s \"ps -ef | grep %s | awk '{print \\$2}' | xargs kill -9\" > /dev/null 2>&1" % (User, storage_host, storage_port)
    print(killStorageProcess)
    start_time = time.time()
    for i in range(500):
        subprocess.run(killStorageProcess, shell=True)
    end_time = time.time()
    print(end_time - start_time)

    #开始检查是否存在’存储节点异常‘, 告警终端管理 -- 逐个检查是否存在存储节点异常
    driver.refresh()
    driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/section/div/div[5]/div/span[2]/div/div/span/span/i').click()#点击页数下拉框
    driver.find_element(By.XPATH, '/html/body/div[2]/div[1]/div[1]/ul/li[4]/span').click()#点击50条/页
    driver.find_element(By.XPATH, '/html/body/div/div/div[1]/div/div[1]/div/ul/div[2]/a/li/span').click()
    alarm_num = driver.find_element(By.XPATH, '/html/body/div/div/div[2]/section/div/div[5]/div/span[1]').text
    alarm_Total_num = re.findall('0|[1-99]', alarm_num)
    print(alarm_Total_num)
    alarm_Total_num = int(alarm_Total_num[0])
    i = 1
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
                break
            print(alarm_Type)
        except:
            print('%s: %s' % (i,alarm_Type))
        i = i + 1

if __name__ == '__main__':
    ps = argparse.ArgumentParser(description='install KunlunBase cluster with Xpanel')
    ps.add_argument('--host', help="Xpanel host", default='192.168.0.125', type=str)
    ps.add_argument('--port', help='Xpanel port', default=18851, type=int)
    ps.add_argument('--user', help="所有涉及到的服务器的通用用户，必须要有ssh互信免密权限",default='kunlun', type=str)
    args = ps.parse_args()
    Host = args.host
    Port = args.port
    User = args.user
    print(args)
    start(Host, Port)
    load_xpanel()
    test()