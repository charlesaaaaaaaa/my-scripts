import argparse
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
import random

def open_windows(host, port):
    global driver
    options = ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    driver = webdriver.Chrome()
    driver.implicitly_wait(5)
    url = 'http://%s:%d/KunlunXPanel/' % (host, port)
    driver.get(url)
    print(url)
    driver.find_element(By.NAME, "username").send_keys('super_dba')
    driver.find_element(By.NAME, 'password').send_keys('Qwer1234.')
    driver.find_element(By.XPATH, '/html/body/div[1]/div/div/form/button/span').click()
    sleep(1)

def dClick(link):
    driver.find_element(By.XPATH, link).click()

def dSend(link, strs):
    driver.find_element(By.XPATH, link).send_keys(strs)

def dClear(link):
    driver.find_element(By.XPATH, link).clear()

def config_node():
    #driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div/div[1]/div/ul/div[1]/li/div').click() # 集群管理
    dClick('/html/body/div[1]/div/div[1]/div/div[1]/div/ul/div[1]/li/ul/div[1]/a/li')#集群列表
    dClick('/html/body/div[1]/div/div[2]/section/div/div/div[1]/div/div/div/div[1]')#集群列表信息
    sleep(2)
    sreach_window = driver.current_window_handle
    dClick('/html/body/div/div/div[2]/section/div/div/div[2]/div[1]/div/div[2]/div[4]/div[2]/table/tbody/tr/td[7]/div/button[4]/span')#点击设置

    def setVar():
        global sql, varName, varValue
        Var = random.randint(1,3)
        #Var = 2
        if Var == 1:
            varName = random.choice(['lock_wait_timeout', 'innodb_lock_wait_timeout', 'fullsync_timeout'])
            varValue = random.randint(1200, 30001)
        elif Var == 2:
            varName = random.choice(['innodb_buffer_pool_size', 'max_binlog_size'])
            varValue = random.randint(1080000000, 1800000000)
        else:
            varName = random.choice(['innodb_flush_log_at_trx_commit', 'sync_binlog', 'global_xmin'])
            varValue = random.randint(0,1)
        sql = 'set global %s = %i' % (varName, varValue)
        print(sql)
        dClick('/html/body/div/div/div[2]/section/div/div/div[2]/div[4]/div/div[1]/div/ul/li[12]')  # 设置实例变量
        dClear('/html/body/div/div/div[2]/section/div/div/div[2]/div[4]/div/div[2]/div/form/div[3]/div/div[1]/input')
        dSend('/html/body/div/div/div[2]/section/div/div/div[2]/div[4]/div/div[2]/div/form/div[3]/div/div[1]/input', sql)#填写变量名
        dClick('/html/body/div/div/div[2]/section/div/div/div[2]/div[4]/div/div[2]/div/form/div[4]/div/button/span')#点击保存

    def getVar():
        global alertText,expected_result
        sql = 'show global variables like "%s"' % (varName)
        dClick('/html/body/div/div/div[2]/section/div/div/div[2]/div[4]/div/div[1]/div/ul/li[13]/span')  # 获取实例变量
        dClear('/html/body/div/div/div[2]/section/div/div/div[2]/div[4]/div/div[2]/div/form/div[3]/div/div[1]/input')
        dSend('/html/body/div/div/div[2]/section/div/div/div[2]/div[4]/div/div[2]/div/form/div[3]/div/div[1]/input',sql)#输入变量名
        dClick('/html/body/div[1]/div/div[2]/section/div/div/div[2]/div[4]/div/div[2]/div/form/div[4]/div/button/span')#点击保存
        alertText = driver.find_element(By.XPATH, '/html/body/div[5]/p').get_attribute('innerHTML')
        expected_result = "获取实例变量成功,value=%s" % (varValue)

    failTimes = 0
    for i in range(3):
        print("========================\n第 %s 次获取结果\n========================" % (i+1))
        setVar()
        sleep(2)
        getVar()
        try:
            assert alertText == expected_result
            print("--------\n实际结果与预期结果相符，成功\n--------")
            print("预期结果: %s" % (expected_result))
        except:
            if alertText == '正在获取实例变量...':
                pass
            else:
                print("--------\n实际结果与预期结果不符，失败\n--------")
                print("预期结果: %s" % (expected_result))
                failTimes = failTimes + 1
        finally:
            print("实际结果: %s" % (alertText))
            while alertText == '正在获取实例变量...':
                print('重新获取实例变量...')
                sleep(1)
                getVar()
                if alertText != expected_result and alertText != '正在获取实例变量...':
                    print('--------\n实际结果与预期结果不符，失败\n--------')
                    print("预期结果: %s" % (expected_result))
                    print("实际结果: %s" % (alertText))
                    failTimes = failTimes + 1
                elif alertText == expected_result:
                    print('--------\n实际结果与预期结果相符，成功\n--------')
                    print("预期结果: %s" % (expected_result))
                    print("实际结果: %s" % (alertText))
        sleep(3)

    if failTimes == 0:
        print("三次设置变量都成功，通过测试")
    else:
        print("三次设置变量中，有 %s 次变量值与实际不符，失败" % (failTimes))
        exit(1)

if __name__ == '__main__':
    ps = argparse.ArgumentParser(description='KunlunBase cluster config with Xpanel')
    ps.add_argument('--host', help="Xpanel host", default='192.168.0.167', type=str)
    ps.add_argument('--port', help='Xpanel port', default=18851, type=int)
    args = ps.parse_args()
    Host = args.host
    Port = args.port
    print(args)
    open_windows(Host, Port)
    config_node()