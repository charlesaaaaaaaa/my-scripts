import time
from selenium.webdriver.common.action_chains import ActionChains
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bin.other_opt import *


class seleniumOpt():
    def __init__(self):
        conf = getconf().getXpanelInfo()
        host = conf['host']
        port = conf['port']
        urls = 'http://%s:%d/KunlunXPanel' % (host, int(port))
        print('\n打开 %s ...' % urls)
        options = ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        ch_options = Options()
        ch_options.add_argument('--no-sandbox')
        ch_options.add_argument('--disable-gpu')
        ch_options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome()
        driver.implicitly_wait(5)
        driver.get(urls)

        self.driver = driver

    def click_Xpath(self, elements):
        driver = self.driver
        driver.find_element(By.XPATH, elements).click()

    def click_Name(self, elements):
        driver = self.driver
        driver.find_element(By.NAME, elements).click()

    def send_Xpath(self, elements, txt):
        driver = self.driver
        driver.find_element(By.XPATH, elements).send_keys(txt)

    def clearAndSend_Xpath(self, elements, txt):
        driver = self.driver
        driver.find_element(By.XPATH, elements).clear()
        driver.find_element(By.XPATH, elements).send_keys(txt)

    def clear_Xpath(self, elements):
        driver = self.driver
        try:
            driver.find_element(By.XPATH, elements).clear()
        except:
            print('clear failure')

    def gettxt_Xpanth(self, elements):
        driver = self.driver
        try:
            txt = driver.find_element(By.XPATH, elements).get_attribute('innerHTML')
            assert txt != ''
            return txt
        except:
            txt = driver.find_element(By.XPATH, elements).text
            return txt

    def getAlert_info(self):
        driver = self.driver
        txt = driver.switch_to.alert.text
        return txt

    def reflush(self):
        driver = self.driver
        driver.refresh()

    def moveToXpanth(self, element):
        driver = self.driver
        element = driver.find_element(By.XPATH, element)
        driver.execute_script("arguments[0].scrollIntoView();", element)
