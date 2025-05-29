from bin.selenium_opt import *
from xpanel_case.load import *
from bin.other_opt import *
from xpanel_case.cluster_manage import *
from xpanel_case.alarm_server import *

resList = []
def genResList(res):
    global resList
    tmp = res
    tmpRes = [tmp[0], tmp[1]]
    resList.append(tmpRes)
    return resList

@timer
def test():
    # 先把所有的元数据节点信息放到一个配置文件里面去
    init_config()
    # 这里放case用例
    # 注意case要返回一个列表，列表第0个元素是用例名，第1个元素是0或者1，0代表失败，1代表成功
    # 没有返回的结果列表的case不要用genResList函数
    loading().load_and_change_pwd()
    genResList(cluster_list().add_new_cluster())
    genResList(cluster_list().add_storage())
    genResList(cluster_list().add_comp())
    genResList(cluster_list().add_shard())
    genResList(cluster_list().del_shard())
    genResList(cluster_list().del_comp())
    genResList(cluster_list().del_replica())
    genResList(cluster_list().rebuild_node())
    genResList(cluster_list().manual_swich_master())
    genResList(cluster_list().unswitch_setting())
    genResList(cluster_list().delete_all_cluster())
    genResList(cluster_list().manual_backup())
    genResList(cluster_list().manual_restron())
    genResList(cluster_list().logic_backup())
    genResList(cluster_list().logic_restore())
    # genResList(cluster_list().config_variables())
    # genResList(cluster_list().monitor())
    # genResList(cluster_list().tmp())
    # genResList(alarm_test().start_alarm())
    res = resList
    return res


def getRes():
    res = test()
    succ, fail = [], []
    for i in res:
        if i[1] == 1:
            succ.append(i[0])
        elif i[1] == 0:
            fail.append(i[0])
    result = {'succ': succ, 'fail': fail}
    return result

if __name__ == "__main__":
    init_config()
    res = getRes()
    totalLen = len(res['succ']) + len(res['fail'])
    print('\n======== 测试结果 ========')
    print('当前测试共 %s 项， 成功 %s 项， 失败 %s 项.' % (totalLen, len(res['succ']), len(res['fail'])))
    print('成功项：%s' % res['succ'])
    print('失败项：%s' % res['fail'])
    print('======== 测试结果 ========')
    if totalLen == len(res['succ']):
        exit(0)
    else:
        exit(1)

