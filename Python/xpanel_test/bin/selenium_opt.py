import time
from selenium.webdriver.common.action_chains import ActionChains
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.keys import Keys
from bin.other_opt import *


class seleniumOpt():
    def __init__(self):
        conf = getconf().getXpanelInfo()
        host = conf['host']
        port = conf['port']
        urls = 'http://%s:%d/KunlunXPanel' % (host, int(port))
        # urls = 'http://%s:%d/#/login' % (host, int(port))
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
        # driver.fullscreen_window()
        self.driver = driver
        # self.fullscreen_window = driver.fullscreen_window()

    def click_Xpath(self, elements, index=None):
        driver = self.driver
        try:
            target_ele = driver.find_element(By.XPATH, elements)
            if index:
                target_ele = driver.find_elements(By.XPATH, elements)
                target_ele = target_ele[index]
            target_ele.click()
            res = 1
        except Exception as err:
            print(elements)
            print('Xpath not exists!')
            res = 0
        return res

    def click_class(self, class_name, index=None):
        driver = self.driver
        target_ele = driver.find_element(By.CLASS_NAME, class_name)
        if index:
            target_ele = driver.find_elements(By.CLASS_NAME, class_name)
            target_ele = target_ele[index]
        target_ele.click()

    def click_Name(self, elements):
        driver = self.driver
        try:
            driver.find_element(By.NAME, elements).click()
        except:
            raise 'Xpath not exists! "%s"' % elements

    def send_Xpath(self, elements, txt, index=None, print_err=0):
        driver = self.driver
        try:
            target = driver.find_element(By.XPATH, elements)
            if index:
                target = driver.find_elements(By.XPATH, elements)
                target = target[index]
            target.send_keys(txt)
            return 1
        except Exception as err:
            if print_err == 1:
                print('%s 不存在' % elements)
            return 0

    def clearAndSend_Xpath(self, elements, txt, index=None, print_err=0):
        driver = self.driver
        try:
            target_ele = driver.find_element(By.XPATH, elements)
            if index:
                target_ele = driver.find_elements(By.XPATH, elements)
                target_ele = target_ele[index]
            target_ele.clear()
            target_ele.send_keys(txt)
            return 1
        except Exception as err:
            if print_err == 1:
                print('%s 不存在' % elements)
            return 0

    def clear_send_css(self, css_element, txt, index=None, print_err=0):
        driver = self.driver
        try:
            target_ele = driver.find_element(By.CLASS_NAME, css_element)
            if index:
                target_ele = driver.find_elements(By.CLASS_NAME, css_element)
                target_ele = target_ele[index]
            target_ele.clear()
            target_ele.send_keys(txt)
            return 1
        except Exception as err:
            if print_err == 1:
                print('%s 不存在' % css_element)
            return 0

    def clear_Xpath(self, elements):
        driver = self.driver
        try:
            driver.find_element(By.XPATH, elements).clear()
        except:
            print('clear failure')

    def gettxt_Xpanth(self, elements, index=None):
        driver = self.driver
        cont_mark = 0
        txt = ''
        try:
            target_ele = driver.find_element(By.XPATH, elements)
            if index:
                target_ele = driver.find_elements(By.XPATH, elements)
                target_ele = target_ele[index]
            txt = target_ele.get_attribute('innerHTML')
            assert txt != ''
            return txt
        except Exception as err:
            cont_mark = 1
        if cont_mark == 1:
            try:
                target_ele = driver.find_element(By.XPATH, elements)
                if index:
                    target_ele = driver.find_elements(By.XPATH, elements)
                    target_ele = target_ele[index]
                txt = target_ele.text
                cont_mark = 0
            except Exception as err:
                # print(str(err))
                err = elements + ' xPaTh FaIl'
                print(err)
                return 0
        return txt

    def getAlert_info(self):
        driver = self.driver
        txt = driver.switch_to.alert.text
        return txt

    def reflush(self):
        driver = self.driver
        driver.refresh()

    def scrollIntoView_Xpath(self, element):
        driver = self.driver
        element = driver.find_element(By.XPATH, element)
        driver.execute_script("arguments[0].scrollIntoView();", element)

    def moveToXpanth(self, element):
        driver = self.driver
        actions = ActionChains(driver)
        element = driver.find_element(By.XPATH, element)
        actions.move_to_element(element).perform()

    def close(self):
        self.driver.close()
        self.driver.quit()

    def select_listopt_element(self, start_part, change_part, end_part, txt_info, click_end_part=None):
        # 这个方法就是用于点击一些下拉框里面的列表选项时用的，以下说明以/html/body/div[5]/div[1]/div[3]/div[1]/ul/li[1]/span为例
        # start_part 就是这个列表选项element的前面不会变化的那一部分xpath，如例子里面的/html/body/div[5]/div[1]/div[3]/div[1]/ul/
        # change_part 就是这个element 里面会变化的那一个标签， 如例子里面会变化的 li 标签，注意不要加上[]， 列表时一般是li，表格时一般是div会变化
        # end_part 就是最后的不会变化的部分， 如例子里面的/span
        # txt_info 就是在这一堆列表里面想要点击的这个选项名，不一定要完全一样，如选项里面有个system(klustron) 就可以指定为system/klustron/system(klustron)
        # click_end_part: 这个比较少用，有的时候txt部分和单选框的那个元素不一样的，但前面的不变的部分和改变的标签元素是一样的情况下就可以用
        # 假设上面的例子里面是一个多选的列表，示例的只是其文本元素定位，当为单选框或者多选框的时候要把最后的/span改为/div[1]/div/i时就可以指定为/div[1]/div/i
        res = 1
        num, txt, tmp_ele = 1, '', ''
        sleep(1)
        try:
            tmp_ele = '%s%s%s' % (start_part, change_part, end_part)
            txt = self.gettxt_Xpanth(tmp_ele)
            if click_end_part:
                tmp_ele = '%s%s%s' % (start_part, change_part, click_end_part)
            assert txt_info in txt
        except Exception as err:
            while txt_info not in txt and num <= 50:
                tmp_ele = '%s%s[%s]%s' % (start_part, change_part, num, end_part)
                txt = self.gettxt_Xpanth(tmp_ele)
                if click_end_part:
                    tmp_ele = '%s%s[%s]%s' % (start_part, change_part, num, click_end_part)
                num += 1
        if num > 50 and txt_info not in txt:
            print('检查超过50次，请检查xpath是否正确！')
            res = 0
        else:
            print('点击[%s]' % txt)
            self.click_Xpath(tmp_ele)
        return res


