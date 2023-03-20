import argparse
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
import random

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

def open_windows(host, port):
    global driver
    options = ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    #这部分是linux的无头模式
    s=Service('./chromedriver')
    ch_options = Options()
    #ch_options.add_argument("--headless")
    ch_options.add_argument('--no-sandbox')
    ch_options.add_argument('--disable-gpu')
    ch_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=ch_options)
    
    #options = ChromeOptions()
    #options.add_experimental_option('excludeSwitches', ['enable-automation'])
    #driver = webdriver.Chrome(executable_path='./chromedriver')
    driver.implicitly_wait(30)
    url = 'http://%s:%d/KunlunXPanel/' % (host, port)
    driver.get(url)
    print(url)
    sreach_window = driver.current_window_handle
    driver.find_element(By.NAME, "username").send_keys('super_dba')
    driver.find_element(By.NAME, 'password').send_keys('Qwer1234.')
    driver.find_element(By.XPATH, '/html/body/div[1]/div/div/form/button/span').click()
    sleep(1)

def dClick(link):
    driver.find_element(By.XPATH, link).click()

def dSend(link, strs):
    driver.find_element(By.XPATH, link).send_keys(strs)

def config_node():
    #driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div/div[1]/div/ul/div[1]/li/div').click() # 集群管理
    dClick('/html/body/div[1]/div/div[1]/div/div[1]/div/ul/div[1]/li/ul/div[1]/a/li')#集群列表
    dClick('/html/body/div[1]/div/div[2]/section/div/div/div[1]/div/div/div/div[1]')#集群列表信息
    sleep(2)
    sreach_window = driver.current_window_handle
    dClick('/html/body/div/div/div[2]/section/div/div/div[2]/div[1]/div/div[2]/div[4]/div[2]/table/tbody/tr/td[7]/div/button[4]/span')#点击设置
    dClick('/html/body/div/div/div[2]/section/div/div/div[2]/div[4]/div/div[1]/div/ul/li[12]')#设置实例变量
    dClick('/html/body/div[1]/div/div[2]/section/div/div/div[2]/div[4]/div/div[2]/div/form/div[3]/div/div/div/input')#shard名称
    dClick('/html/body/div[2]/div[1]/div[1]/ul/li')#选择shard_1
    dClick('/html/body/div[1]/div/div[2]/section/div/div/div[2]/div[4]/div/div[2]/div/form/div[4]/div/div/div/input')#节点
    dClick('/html/body/div[3]/div[1]/div[1]/ul/li[1]/span') #选择第一个节点
    dClick('/html/body/div[1]/div/div[2]/section/div/div/div[2]/div[4]/div/div[2]/div/form/div[5]/div/div/div/input')#变量类型
    dClick('/html/body/div[4]/div[1]/div[1]/ul/li[1]')#选择int类型
    varName = random.choice(['lock_wait_timeout', 'innodb_lock_wait_timeout'])
    varValue = random.randint(1200, 3001)
    dSend('/html/body/div[1]/div/div[2]/section/div/div/div[2]/div[4]/div/div[2]/div/form/div[6]/div/div[1]/input', varName)#填写变量名
    dSend('/html/body/div[1]/div/div[2]/section/div/div/div[2]/div[4]/div/div[2]/div/form/div[7]/div/div[1]/input', varValue)#填写变量值
    dClick('/html/body/div[1]/div/div[2]/section/div/div/div[2]/div[4]/div/div[2]/div/form/div[8]/div/button/span')#点击保存

    dClick('/html/body/div/div/div[2]/section/div/div/div[2]/div[4]/div/div[1]/div/ul/li[13]')#获取实例变量
    sreach_window = driver.current_window_handle
    dClick('/html/body/div[1]/div/div[2]/section/div/div/div[2]/div[4]/div/div[2]/div/form/div[3]/div/div/div/span')#shard名称
    dClick('/html/body/div[2]/div[1]/div[1]/ul/li')#选择shard1
    dClick('/html/body/div[1]/div/div[2]/section/div/div/div[2]/div[4]/div/div[2]/div/form/div[4]/div/div/div/span/span/i')#节点
    dClick('/html/body/div[3]/div[1]/div[1]/ul/li[1]')#选择节点1
    dSend('/html/body/div[1]/div/div[2]/section/div/div/div[2]/div[4]/div/div[2]/div/form/div[5]/div/div[1]/input',varName)#输入变量名
    dClick('/html/body/div[1]/div/div[2]/section/div/div/div[2]/div[4]/div/div[2]/div/form/div[6]/div/button')#点击保存
    alertText = driver.find_element(By.XPATH, '/html/body/div[5]/p').get_attribute('innerHTML')
    driver.refresh()
    expected_result = "获取实例变量成功,value=%s" % (varValue)
    try:
        assert alertText == expected_result
    except:
        print("========\n实际结果与预期结果不符，失败\n========")
        print("预期结果: %s" % (expected_result))
        exit(1)
    finally:
        print("实际结果: %s" % (alertText))
    sleep(5)

if __name__ == '__main__':
    ps = argparse.ArgumentParser(description='KunlunBase cluster config with Xpanel')
    ps.add_argument('--host', help="Xpanel host", default='192.168.0.132', type=str)
    ps.add_argument('--port', help='Xpanel port', default=18851, type=int)
    args = ps.parse_args()
    Host = args.host
    Port = args.port
    print(args)
    open_windows(Host, Port)
    config_node()
