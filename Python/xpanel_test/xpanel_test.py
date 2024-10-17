from bin.selenium_opt import *
from xpanel_case.load import *
from xpanel_case.cluster_manage import *

resList = []
def genResList(res):
    global resList
    tmp = res
    tmpRes = [tmp[0], tmp[1]]
    resList.append(tmpRes)
    return resList

def test():
    # 这里放case用例
    # 注意case要返回一个列表，列表第0个元素是用例名，第1个元素是0或者1，0代表失败，1代表成功
    # 没有返回的结果列表的case不要用genResList函数
    loading().load_and_change_pwd()
    loading().load_and_change_pwd()
    genResList(cluster_list().add_new_cluster())
    genResList(cluster_list().add_repartition())
    genResList(cluster_list().add_comp())
    genResList(cluster_list().del_comp())
    genResList(cluster_list().del_replica())
    genResList(cluster_list().rebuild_node())
    genResList(cluster_list().manual_swich_master())
    genResList(cluster_list().delete_all_cluster())
    genResList(cluster_list().config_variables())
    # genResList(cluster_list().monitor())
    # genResList(cluster_list().tmp())
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

