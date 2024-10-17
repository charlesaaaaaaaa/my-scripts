from xpanel_case.load import *
from bin.other_opt import *
import random

class multi_tenancy_test():
    def __init__(self):
        self.driver = loading().load()
        self.ele = getElements().multi_tenan()

    @timer
    def click_register_and_login_couple_times(self):
        # 多次点击 [注册] 和 [去登录] 按钮
        ele = self.ele
        driver = self.driver
        # driver函数会先登录超级用户，要先 [退出] 超级用户
        driver.click_Xpath(ele['logout'])
        # 现在是在登录界面
        times = random.randint(500, 2000)
        print('开始循环点击注册及登录按钮 [%s] 次' % times)
        for i in range(times):
            # 要点击 [注册]
            print('\r第 %s/%s 次 ……' % (i + 1, times), end='')
            driver.click_Xpath(ele['register'])
            # 进入注册界面再点 [去登录]
            driver.click_Xpath(ele['go_login'])

    @timer
    def register_many_times(self):
        # 暴力注册
        driver = self.driver
        ele = self.ele
        # [登出] 超级用户
        driver.click_Xpath(ele['logout'])
        # 现在是在登录界面, 开始循环 [注册], 给个随机数
        times = random.randint(200, 2000)
        for i in range(times):
            if i < 10:
                user_num = '000%s' % i
            # elif i < 100 and i >= 10:
            elif i < 100:
                user_num = '00%s' % i
            # elif i < 1000 and i >= 100:
            elif i < 1000:
                user_num = '0%s' % i
            else:
                user_num = i
            user_name = 'user%s' % user_num
            user_pass = 'User%s' % user_num
            print('registering for [%s] ……' % user_name)
            # 点击 [注册]
            driver.click_Xpath(ele['register'])
            # 输入 [用户名] [用户密码] [确认用户密码]
            driver.send_Xpath(ele['register_user_name_input'], user_name)
            driver.send_Xpath(ele['register_user_pass_1_input'], user_pass)
            driver.send_Xpath(ele['register_user_pass_2_input'], user_pass)
            # 点击 [确认注册]
            driver.click_Xpath(ele['register_done_button'])

    @timer
    def reguler_test(self, admin_num, user_count):
        # 第一个参数是管理员的号数，其账号为'Test%sAdmin' % admin_num
        # 第二个参数是要新增的用户总数
        ele = self.ele
        driver = self.driver
        # 正常流程
        # 注册一个管理员 - 管理员再新加一个租户 - 新建一个schema并把这个schema的权限给新租户 - 把新租户的连接数随意调整
        # 通过这个租户信息那栏来去后台登录这个租户 - 在对应的schema和没有权限的schema上create table和一些没有权限的操作
        # 删除租户 - 登出管理员 - 登入超级用户删除新建的管理员
        admin_name = 'Test%sAdmin' % admin_num
        admin_pass = 'Test%sAdmin.' % admin_num
        # [退出]超级用户
        driver.click_Xpath(ele['logout'])

        # 点击 [注册]
        driver.click_Xpath(ele['register'])
        # 填写 [用户名] [用户密码] [用户确认密码]
        #sleep(5)
        driver.send_Xpath(ele['register_user_name_input'], admin_name)
        driver.send_Xpath(ele['register_user_pass_1_input'], admin_pass)
        driver.send_Xpath(ele['register_user_pass_2_input'], admin_pass)
        # 点击 [立即注册]
        driver.click_Xpath(ele['register_done_button'])

        # 开始 [登录] 普通管理员
        # 输入 [用户名] [用户密码]
        driver.send_Xpath(ele['login_user'], admin_name)
        driver.send_Xpath(ele['login_pass'], admin_pass)
        # 点击 [登录]
        driver.click_Xpath(ele['login_done'])
        # 点击 [系统管理] - [用户管理]
        driver.click_Xpath(ele['system_manage'])
        driver.click_Xpath(ele['user_manage'])
        range_times = user_count
        delete_xpath = ele['admin_delete_user_range'] + 'tr[2]/td[7]/div/button[2]/span'
        delete_user_name = ele['admin_delete_user_name']
        old_user_num = 0
        while True:
            try:
                user_name = driver.gettxt_Xpanth(delete_user_name)
                print('## try to delete user [%s] ……' % user_name)
                driver.click_Xpath(delete_xpath)
                driver.click_Xpath(ele['admin_delete_user_sbmit_button'])
                old_user_num += 1
            except:
                print('The list of subtenant is empty，delete %s users' % old_user_num)
                break
        for random_num in range(1, range_times + 1):
            # 查看当前所有用户总数
            random_name_lenght = random.randint(8, 12)
            user_name = ''
            len_num = 0
            for i in range(random_name_lenght):
                len_num += 1
                if len_num == 1:
                    chars = random.choice('QWERTYUIOPLKJHGFADSCXZVBNM')
                elif len_num == 2:
                    chars = str(random.randint(0, 9))
                elif len_num == 3:
                    chars = random.choice('qwerasdfzxcvbnmghjktyuilop')
                else:
                    chars = random.choice('1234567890QWERTYUIOPLKJHGFADSCXZVBNMqwerasdfzxcvbnmghjktyuilop')
                user_name += chars
            user_total_counts = driver.gettxt_Xpanth(ele['total_user_counts']).split(' ')[1]
            # 点击 [新增]
            driver.click_Xpath(ele['add_new_user_button'])
            # 输入 [用户名] [用户密码1] [用户密码2] [邮箱]
            #random_num = random.randint(1, 99)
            new_user_name = user_name
            new_user_pass = user_name
            user_mail = '%s@notexist.com' % user_name
            print('## add new subtenant [%s]' % new_user_name)
            driver.send_Xpath(ele['new_user_name'], new_user_name)
            driver.send_Xpath(ele['new_user_pass_1'], new_user_pass)
            driver.send_Xpath(ele['new_user_pass_2'], new_user_pass)
            driver.send_Xpath(ele['new_user_email'], user_mail)
            # 点击 [max connection] 这个选项无了，不知道什么时候重新加进来，先注释着
            # driver.click_Xpath(ele['max_connection_button'])
            # def collect_max_connect_options():
            #     # 开始收集所有最大连接数的选项
            #     max_connect_list = []
            #     level = 0
            #     pre_xpath = ele['max_connection_range']
            #     while True:
            #         level += 1
            #         aft_xpath = 'li[%d]/span' % level
            #         complete_xpath = pre_xpath + aft_xpath
            #         try:
            #             tmp = driver.gettxt_Xpanth(complete_xpath)
            #             max_connect_list.append(tmp)
            #         except:
            #             break
            #     return max_connect_list
            # 获取所有最大连接数选项列表
            # max_connect_list = collect_max_connect_options()
            # print('* 当前最大连接数可以选项列表：\n\t%s' % max_connect_list)
            # random_connection = random.randint(1, len(max_connect_list))
            # # 点击随机后的连接数
            # pre_xpath = ele['max_connection_range']
            # aft_xpath = 'li[%d]/span' % random_connection
            # complete_xpath = pre_xpath + aft_xpath
            # driver.click_Xpath(complete_xpath)
            # 点击 [确定]
            driver.click_Xpath(ele['new_user_done'])
            # 再次检查 当前所有用户总数
            user_total_counts_new = driver.gettxt_Xpanth(ele['total_user_counts']).split(' ')[1]
            if int(user_total_counts_new) != int(user_total_counts) + 1:
                print('ERROR: 新增用户总数出错，\n\t* 新增前：%s\n\t* 新增后：%s' %(user_total_counts, user_total_counts_new))


    @timer
    def compare_with_superuser(self):
        driver = self.driver
        ele = self.ele
        # 开始获取 超级用户的 集群设置的可用选项
        # 点击 [设置]
        driver.click_Xpath(ele['superuser_cluster_setting'])
        def get_setting_options():
            # 开始一个个查找所有的一级选项并放到一个二级列表里面
            # 每个选项各占一级列表的一个元素，这个元素里面是二级列表
            # 第一个是选项名，第二个是该一级选项是否有二级列表，1为有，0为无
            level = 0
            xpath_pre = ele['superuser_cluster_setting_option_range']
            superuser_cluster_setting_options_list = []
            while True:
                level += 1
                xpath_aft = 'li[%d]/span' % level
                try:
                    try:
                        xpath_complete = xpath_pre + xpath_aft
                        option_name = driver.gettxt_Xpanth(xpath_complete)
                        tmp_list = [option_name, 0]
                        superuser_cluster_setting_options_list.append(tmp_list)
                    except:
                        xpath_aft = 'li[%d]/div/span' % level
                        xpath_complete = xpath_pre + xpath_aft
                        option_name = driver.gettxt_Xpanth(xpath_complete)
                        tmp_list = [option_name, 1]
                        superuser_cluster_setting_options_list.append(tmp_list)
                except:
                    break
            return superuser_cluster_setting_options_list
        superuser_cluster_setting_options_list = get_setting_options()
        print('当前超级用户集群设置所有功能选项为： \n\t%s' % (superuser_cluster_setting_options_list))
        # [登出] 超级用户
        try:
            driver.click_Xpath(ele['logout'])
        except:
            driver.click_Xpath(ele['logout1'])
        # 开始 [登录] 普通管理员
        user_name = 'qwer1234'
        user_pass = 'Qwer1234'
        # 输入 [用户名] [用户密码]
        driver.send_Xpath(ele['login_user'], user_name)
        driver.send_Xpath(ele['login_pass'], user_pass)
        # 点击 [登录]
        driver.click_Xpath(ele['login_done'])
        # 点击 [设置]
        driver.click_Xpath(ele['admin_cluster_setting'])
        admin_cluster_setting_options_list = get_setting_options()
        print('当前普通管理员集群设置所有功能选项为： \n\t%s' % admin_cluster_setting_options_list)
