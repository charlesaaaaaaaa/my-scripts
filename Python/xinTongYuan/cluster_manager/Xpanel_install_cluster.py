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
from multiprocessing import Process
from selenium.webdriver.common.action_chains import ActionChains

def InfoMations(Str): #这个就是动态展示正在做什么用的而已，去掉影响也不大，需要用到多进程
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

def InfoMation(Str):
    while True:
        print('\r%s中////////'% (Str), end='')
        sleep(0.1)
        print('\r%s中--------'% (Str), end='')
        sleep(0.1)
        print('\r%s中\\\\\\\\\\\\\\\\'% (Str), end='')
        sleep(0.1)
        print('\r%s中||||||||'% (Str), end='')
        sleep(0.1)

def start(host, port):#开启driver
    global driver
    urls = 'http://%s:%d/KunlunXPanel' % (host, port)
    print(urls)
    options = ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    '''
    #这里被注释的是windows的部分
    #driver = webdriver.Chrome(executable_path='D:\python3\chromedriver.exe')
    #driver = webdriver.Chrome()
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
    driver.get(urls)
    return driver

def change_pwd():
    CP_startTime = time.time()
    thread0 = Process(target=InfoMation, args=(('修改密码'),))
    thread0.start()
    driver.find_element(By.NAME, "username").send_keys('super_dba')
    driver.find_element(By.NAME, 'password').send_keys('super_dba')
    driver.find_element(By.XPATH, '//*[@id="app"]/div/div/form/button/span').click()
    try:
        sleep(0.5)
        wrg = driver.find_element(By.XPATH, '/html/body/div/div/div/form/div[1]/h3').text
        assert wrg == '修改密码'
        driver.find_element(By.NAME, 'password').send_keys('Qwer1234.')
        driver.find_element(By.NAME, 'confirmPassword').send_keys('Qwer1234.')
        driver.find_element(By.XPATH, '/html/body/div[1]/div/div/form/button/span').click()
        #txt = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/form/button/span').text
        #while wrg == '修改密码':
            #driver.find_element(By.XPATH, '/html/body/div[1]/div/div/form/button/span').click()

        thread0.terminate()
    except:
        thread0.terminate()
        print('\r修改密码中 ...非首次登录，跳过...', end='')
        driver.refresh()
        #for i in range(10):
        driver.find_element(By.NAME, 'username').clear()
        driver.find_element(By.NAME, 'password').clear()
        sleep(0.5)
    finally:
        print('\r修改密码中 ...完成...          ')
    sleep(1)
    CP_endTime = time.time()
    print('修改密码使用了%.2f秒' % (CP_endTime - CP_startTime))
    
def load_xpanel():
    sleep(3)
    load_startTime = time.time()
    thread1 = Process(target=InfoMation, args=(('登录'),))
    thread1.start()
    driver.find_element(By.NAME, "username").send_keys('super_dba')
    driver.find_element(By.NAME, 'password').send_keys('Qwer1234.')
    driver.find_element(By.XPATH, '//*[@id="app"]/div/div/form/button/span').click()
    sleep(1)
    thread1.terminate()
    load_endTime = time.time()
    print('\r登录中 完成     ')
    print('本次登录使用了 %.2f 秒' % (load_endTime - load_startTime))

def create_cluster():
    create_startTime = time.time()
    thread2 = Process(target=InfoMation, args=(('创建集群'),))
    thread2.start()
    sleep(2)
    #driver.find_element(By.XPATH,'/html/body/div[1]/div/div[2]/section/div/div/div[2]/div[1]/div/div[4]/div/div[2]/form/div[2]/div/div/div[1]/div/div/div/div[1]').click() #点击本地集群
    driver.find_element(By.XPATH,'/html/body/div/div/div[2]/section/div/div/div[2]/div[1]/div/div[1]/div/button[3]').click() #点击新增
    driver.find_element(By.XPATH,'/html/body/div[1]/div/div[2]/section/div/div/div[2]/div[1]/div/div[4]/div/div[2]/form/div[1]/div/div[1]/input').send_keys('test') #写入业务名称
    driver.find_element(By.XPATH,'/html/body/div[1]/div/div[2]/section/div/div/div[2]/div[1]/div/div[4]/div/div[2]/form/div[2]/div/div/div[2]/div[1]/div[1]/div/div[2]/input').click() #点击存储
    for i in range(1, StorageNum + 1): # 开始选择对应的存储节点
        try:
            eleStorageM1 = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/section/div/div/div[2]/div[1]/div/div[4]/div/div[2]/form/div[2]/div/div/div[2]/div[1]/div[1]/div/div[3]/div[1]/div[1]/ul/li[%s]/span' % str(i))
            driver.execute_script('arguments[0].click();', eleStorageM1)
        except Exception as r:
            print("无法找到第%d个storage_node" % (i))
            print(sys.exc_info())
    sleep(1)
    driver.find_element(By.XPATH,'/html/body/div[1]/div/div[2]/section/div/div/div[2]/div[1]/div/div[4]/div/div[2]/form/div[2]/div/div/div[2]/div[1]/div[1]/div/div[2]/span/span/i').click() #缩回下拉框
    driver.find_element(By.XPATH,'/html/body/div[1]/div/div[2]/section/div/div/div[2]/div[1]/div/div[4]/div/div[2]/form/div[2]/div/div/div[2]/div[1]/div[2]/div/div[2]/input').click() #点击计算节点
    for i in range(1, ServerNum + 1):
        try:
            eleCompM = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/section/div/div/div[2]/div[1]/div/div[4]/div/div[2]/form/div[2]/div/div/div[2]/div[1]/div[2]/div/div[3]/div[1]/div[1]/ul/li[%s]/span' % (i))
            driver.execute_script("arguments[0].click();", eleCompM)
        except Exception as r:
            print("无法找到第%d个server_node" % (i))
            print(sys.exc_info())
    sleep(1)
     #input shard info
    driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/section/div/div/div[2]/div[1]/div/div[4]/div/div[2]/form/div[5]/div/div/div/input').clear()
    driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/section/div/div/div[2]/div[1]/div/div[4]/div/div[2]/form/div[5]/div/div/div/input').send_keys('%d' % (ShardNum))
    driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/section/div/div/div[2]/div[1]/div/div[4]/div/div[2]/form/div[6]/div/div/input').clear()
    driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/section/div/div/div[2]/div[1]/div/div[4]/div/div[2]/form/div[6]/div/div/input').send_keys('%d' % (ReplicaNum))
    driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/section/div/div/div[2]/div[1]/div/div[4]/div/div[2]/form/div[7]/div/div/input').clear()
    driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/section/div/div/div[2]/div[1]/div/div[4]/div/div[2]/form/div[7]/div/div/input').send_keys('%d' % (ServerNum))
    try:
        driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/section/div/div/div[2]/div[1]/div/div[4]/div/div[2]/form/div[12]/div/div[1]/input').send_keys('1024')
        driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/section/div/div/div[2]/div[1]/div/div[4]/div/div[2]/form/div[13]/div/div/input').send_keys('1024')
    except:
        print('\nconnot find element -- storage log num, skip')
    driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/section/div/div/div[2]/div[1]/div/div[4]/div/div[3]/div/button[2]/span').click()

    # 这部分是在等待并检测集群是否新建成功
    Count = 1
    while True:
        texts = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/section/div/div/div[2]/div[1]/div/div[13]/div/div[2]/div/div/div[3]/div[2]/div[1]')
        txt = texts.text
        try:
            assert txt == '新增集群成功'
            thread2.terminate()
            print('\r创建集群中 %s        ' % (txt))
            create_endTime = time.time()
            create_spendTime = create_endTime-create_startTime
            print('本次创建集群花费了 %.2f 秒' % (create_spendTime))
            return(txt)
            break
        except:
            if txt == '新增集群失败':
                thread2.terminate()
                print('\r创建集群中 %s     ' % (txt))
                return(txt)
                break
            else:
                continue
        finally:
            Count = Count + 1
            if Count == 900:
                thread2.terminate()
                print('\r创建集群中 新建集群超时(15m), 失败             ')
                break
            sleep(1)
    
    create_endTime = time.time()
    create_spendTime = create_endTime-create_startTime

if __name__ == '__main__':
    ps = argparse.ArgumentParser(description='install KunlunBase cluster with Xpanel')
    ps.add_argument('--host', help="Xpanel host", default='192.168.0.167', type=str)
    ps.add_argument('--port', help='Xpanel port', default=18851, type=int)
    ps.add_argument('--shardNum', help='KunlunBase cluster shard num, shard num >= 1', type=int, default=2)
    ps.add_argument('--replicaNum', help='KunlunBase cluster replica Num, replica num >=3', type=int, default=3)
    ps.add_argument('--serverNum', help='KunlunBase cluster Kunlun-server num >= 1', type=int, default=3)
    ps.add_argument('--storageNum', help='拿出多少台服务器给存储节点使用，数量大于等于1', type=int, default=3)
    args = ps.parse_args()
    Host = args.host
    Port = args.port
    ShardNum = args.shardNum
    ReplicaNum = args.replicaNum
    ServerNum = args.serverNum
    StorageNum = args.storageNum
    print(args)
    start_time = time.time()
    start(Host, Port)
    change_pwd()
    load_xpanel()
    create_cluster()
    driver.quit()
    end_time = time.time()
    spend_time = end_time - start_time
    print("本次花费了 %.2f 秒" % (spend_time))
