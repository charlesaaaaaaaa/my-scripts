from bin.selenium_opt import *
from bin.other_opt import *


class loading():
    #这个是登录且修改密码
    def __init__(self):
        self.driver = seleniumOpt()
        self.conf = getElements()
        self.xpanelInfo = getconf().getXpanelInfo()

    @timer
    def load_and_change_pwd(self):
        driver = self.driver
        conf = self.conf
        xlanelInfo = self.xpanelInfo
        elements = conf.loadInterface()
        name = elements['user']
        password = elements['password']
        print('正在尝试 登录并修改 xpanel初始用户密码')
        try:
            try:
                driver.send_Xpath(name, 'super_dba')
                driver.send_Xpath(password, 'super_dba')
                driver.click_Xpath(elements['commit_button'])
                driver.send_Xpath(elements['new_pwd'], xlanelInfo['password'])
                # driver.send_Xpath(elements['new_pwd_again'], xlanelInfo['password'])
                # driver.click_Xpath(elements['change_button'])
            except:
                print('当前无法修改密码，是否已经修改过？')
                sleep(3)
                driver.click_Xpath(elements['commit_button'])
                driver.send_Xpath(elements['new_pwd'], xlanelInfo['password'])
            finally:
                driver.send_Xpath(elements['new_pwd_again'], xlanelInfo['password'])
                driver.click_Xpath(elements['change_button'])
        except:
            pass

    def load(self):
        driver = self.driver
        elements = self.conf.loadInterface()
        xpanelInfo = self.xpanelInfo
        sleep(1)
        driver.send_Xpath(elements['user'], xpanelInfo['user'])
        driver.send_Xpath(elements['password'], xpanelInfo['password'])
        driver.click_Xpath(elements['commit_button'])
        return driver




















