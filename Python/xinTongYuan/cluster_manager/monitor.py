import time
from selenium import webdriver
from time import sleep
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import argparse

def InfoMation(Str): #这个就是动态展示正在做什么用的而已，去掉影响也不大，需要用到多进程
    Values = '%s中...' % (Str)
    Count = 1
    while True:
        Values = '%s' % (Values)
        if Count <= 3:
            print('\r%s' % (Values), end='')
            Count = Count + 1
            sleep(1)
        elif Count > 3 and Count < 10 :
            Values = '%s%s' % (Values, '.')
            print('\r%s' % (Values), end='')
            Count = Count + 1
            sleep(1)
        else :
            Values = '%s中...         ' % (Str)
            print('\r%s' % (Values), end='')
            Values = '%s中...' % (Str)
            print('\r%s' % (Values), end='')
            Count = 0;
            sleep(1)

def open(host, port):
    global driver
    options = ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    #chrome_options.add_argument('--headless')
    s = Service('./chromedriver')
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.implicitly_wait(30)
    url = 'http://%s:%d/KunlunXPanel/' % (host, port)
    driver.get(url)
    print(url)
    sreach_window = driver.current_window_handle
    driver.find_element(By.NAME, "username").send_keys('super_dba')
    driver.find_element(By.NAME, 'password').send_keys('Qwer1234.')
    driver.find_element(By.XPATH, '//*[@id="app"]/div/div/form/button/span').click()
    sleep(1)

def dClick(link):
    driver.find_element(By.XPATH, link).click()

def dSend(link, strs):
    driver.find_element(By.XPATH, link).send_keys(strs)

def enter_shard_list():
    dClick('/html/body/div[1]/div/div[1]/div/div[1]/div/ul/div[1]/li/ul/div[1]/a/li/span')  # 集群列表
    dClick('/html/body/div[1]/div/div[2]/section/div/div/div[1]/div/div/div/div[1]')  # 集群列表信息
    dClick(
        '/html/body/div/div/div[2]/section/div/div/div[2]/div[1]/div/div[2]/div[4]/div[2]/table/tbody/tr/td[7]/div/button[4]')  # 点击设置
    sleep(1)
    dClick('/html/body/div/div/div[2]/section/div/div/div[2]/div[4]/div/div[1]/div/ul/li[10]/span')  # 计算节点列表
    dClick('/html/body/div/div/div[2]/section/div/div/div[2]/div[4]/div/div[1]/div/ul/li[9]/span')  # shard列表

def show_monitor():
    enter_shard_list()
    for nodeNum in range(1,3): #这一步就是在选择备节点的机器的禁用button
        shard1_node2 = '/html/body/div/div/div[2]/section/div/div/div[2]/div[4]/div/div[2]/div/div[2]/div[3]/table/tbody/tr[2]/td/div/div[3]/table/tbody/tr[%d]/td[8]/div/button[3]/span' % (nodeNum)
        testText = driver.find_element(By.XPATH, shard1_node2).text
        print('node_%s: %s' % (nodeNum, testText))
        if testText == '禁用':
            break
        else :
            shard1_node2 = ''
    print('开始禁用备节点：node_%s...' % (nodeNum))
    dClick(shard1_node2)#点击备节点的禁用button
    warnText = driver.find_element(By.XPATH, '/html/body/div[2]/div/div[2]/div[1]/div[2]/p').get_attribute('innerHTML')#这里在获取弹窗的提示语
    warnText = warnText.split('=', -1)#以‘=‘为分隔符，把提示语分成多个字符并赋给到一个列表里
    verCode = str(warnText[-1])#把列表最后一个值给到verCode，最后一个值就是我们要的验证码
    dSend('/html/body/div[2]/div/div[2]/div[2]/div[1]/input',verCode)#输入验证码
    dClick('/html/body/div[2]/div/div[3]/button[2]/span')#确定禁用

    #验证是否禁用成功
    while True:
        try:
            Alerts = '/html/body/div[1]/div/div[2]/section/div/div/div[2]/div[4]/div/div[2]/div/div[6]/div/div[2]/div/ul/li[2]/div[3]/div[1]'
            txt = driver.find_element(By.XPATH, Alerts).get_attribute('innerHTML')
            print(txt)
            assert txt == ' 禁用成功 '
            break
        except:
            if txt == ' 禁用失败':
                print(Alerts)
                exit(1)
            else:
                sleep(1)

    dClick('/html/body/div[1]/div/div[2]/section/div/div/div[2]/div[4]/div/div[2]/div/div[6]/div/div[1]/button/i')#点击x
    driver.refresh() #刷新当前页面
    sleep(2)
    enter_shard_list()
    nodeAttr = '/html/body/div[1]/div/div[2]/section/div/div/div[2]/div[4]/div/div[2]/div/div[2]/div[3]/table/tbody/tr[2]/td/div/div[3]/table/tbody/tr[%d]/td[7]/div/span' % (nodeNum)
    nodeAttr_text = driver.find_element(By.XPATH, nodeAttr).text #找到被禁用的节点状态
    times = 0
    print('检查node_%s状态：%s' % (nodeNum, nodeAttr_text))
    try:
        assert nodeAttr_text == '停止'
    except:
        sleep(1)
        times = times + 1
        if times == 15:
            print('禁用失败，退出测试')
            exit(1)

    sleep(3)
    print('开始启动备节点：node_%s...'% (nodeNum))
    start_button = '/html/body/div/div/div[2]/section/div/div/div[2]/div[4]/div/div[2]/div/div[2]/div[3]/table/tbody/tr[2]/td/div/div[3]/table/tbody/tr[%d]/td[8]/div/button[1]' % (nodeNum)
    dClick(start_button) #点击刚刚禁用的机器
    start_text = driver.find_element(By.XPATH, '/html/body/div[2]/div/div[2]/div[1]/div[2]/p').get_attribute('innerHTML')# 找到提示语句
    start_text = start_text.split('=', -1)#把提示语句以‘=’号分割，-1就是分割成最大份
    startCode = str(start_text[-1])#获取验证码
    dSend('/html/body/div[2]/div/div[2]/div[2]/div[1]/input', startCode)#把验证码输入到框里
    dClick('/html/body/div[2]/div/div[3]/button[2]')#点击确定
    warnText_start = '/html/body/div[1]/div/div[2]/section/div/div/div[2]/div[4]/div/div[2]/div/div[6]/div/div[2]/div/ul/li[2]/div[3]/div[1]'

    while True:
        try:
            start_result = driver.find_element(By.XPATH, warnText_start).get_attribute('innerHTML') #查看结果
            print(start_result)
            assert start_result == ' 启用成功 '#断言是否为启用成功
            break
        except:
            if start_result == ' 启用失败 ':
                print('启用失败，退出测试')
                exit(1)
            else:
                sleep(1)

    dClick('/html/body/div[1]/div/div[2]/section/div/div/div[2]/div[4]/div/div[2]/div/div[6]/div/div[1]/button/i')#点击x
    driver.refresh()#刷新当前页面
    sleep(1)
    driver.refresh()
    enter_shard_list()
    startAttr = '/html/body/div/div/div[2]/section/div/div/div[2]/div[4]/div/div[2]/div/div[2]/div[3]/table/tbody/tr[2]/td/div/div[3]/table/tbody/tr[%d]/td[7]/div/span[1]' % (nodeNum)
    #startAttr = '/html/body/div/div/div[2]/section/div/div/div[2]/div[4]/div/div[2]/div/div[2]/div[3]/table/tbody/tr[2]/td/div/div[3]/table/tbody/tr[2]/td[7]/div/span[1]'
    nodeAttr_text_start = driver.find_element(By.XPATH, startAttr).get_attribute('innerHTML')
    times = 0
    while True:
        nodeAttr_text_start = driver.find_element(By.XPATH, startAttr).get_attribute('innerHTML')
        print(nodeAttr_text_start)
        try:
            assert nodeAttr_text_start == '运行中'
            break
        except:
            sleep(1)
            driver.refresh()  # 刷新当前页面
            enter_shard_list()
            times = times + 1
            if times == 15:
                print('启动失败，退出测试')
                exit(1)

    print('检查node_%s状态：%s' % (nodeNum, nodeAttr_text_start))
    print('测试完成！退出测试')

if __name__ == '__main__':
    ps = argparse.ArgumentParser(description='KunlunBase cluster monitor with Xpanel')
    ps.add_argument('--host', help="Xpanel host", default='192.168.0.132', type=str)
    ps.add_argument('--port', help='Xpanel port', default=18851, type=int)
    args = ps.parse_args()
    Host = args.host
    Port = args.port
    print(args)
    open(Host, Port)
    show_monitor()
