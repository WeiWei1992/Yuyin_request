import os
import re
import logging
import logging.config
CON_LOG='log.conf'
logging.config.fileConfig(CON_LOG)
logging=logging.getLogger()

import time

def judeg_res_error(baseres,res,sign):
    #当设备离线、未绑定、无此功能时通过改方法校验
    #只校验 category、domain、action
    logging.error("当前设备状态异常，当设备离线、未绑定、无此功能时通过改方法校验")

    fail_reasons = []

    if sign==1:
        fail_reasons.append("设备离线")
    elif sign==2:
        fail_reasons.append("设备未添加")
    elif sign==3:
        fail_reasons.append("设备状态冲突")
    elif sign==4:
        fail_reasons.append("设备未开机")
    elif sign==5:
        fail_reasons.append("设备无此功能")
    # elif sign==7:
    #     fail_reasons.append("没有发现这个设备")


    flag = True
    try:
        # 校验status_code
        logging.info("status_code")
        if res['status_code'] == str(200):
            logging.info("status_code=200，正确")
        else:
            temp_txt = 'status_code不是200。'
            logging.error(temp_txt)
            fail_reasons.append(temp_txt)
            flag = False
    except:
        temp_txt = 'status_code对比异常'
        logging.error(temp_txt)
        fail_reasons.append(temp_txt)
        flag = False

    logging.info("对比category")
    try:
        if baseres['category'] == None:
            logging.warning("baseres['category']为空，略过")
        else:
            if baseres['category'] == res['category']:
                logging.info("category对比正确")
            else:
                temp_txt = " category参数不正确，失败 。"
                logging.error(temp_txt)
                fail_reasons.append(temp_txt)
                flag = False
    except:
        temp_txt = " category对比异常"
        logging.error(temp_txt)
        fail_reasons.append(temp_txt)
        flag = False

    try:
        logging.info("对比domain")
        if baseres['domain'] == None:
            logging.warning("domain参数为空，略过")
        else:
            if baseres['domain'] == res['domain']:
                logging.info("domain参数正确")
            else:
                temp_txt = "domain不正确，失败。"
                fail_reasons.append(temp_txt)
                flag = False
    except:
        temp_txt = "domain对比异常"
        fail_reasons.append(temp_txt)
        flag = False

    try:

        logging.info("对比action")
        if baseres['action'] == None:
            logging.warning("action参数为空，略过")
        else:
            if baseres['action'] == res['action']:
                logging.info("action参数正确")
            else:
                temp_txt = 'action参数不正确，失败。'
                fail_reasons.append(temp_txt)
                flag = False
    except:
        logging.error("action对比失败")
        temp_txt = 'action对比失败'
        fail_reasons.append(temp_txt)
        flag = False

    if sign==6:
        flag=True
        fail_reasons.insert(0,"账号过期，先登录")


    return flag, fail_reasons, res, sign




def judeg_res(baseres,res):
    logging.info("比较用例和返回的数据")
    logging.info("传入的用例是：")
    logging.info(baseres)
    logging.info("传入的请求返回是： ")
    logging.info(res)

    sign = 0

    logging.info("首先判断设备状态是否正常，通过response判断,设备状态异常，当设备离线、未绑定、无此功能")
    # 离线情况
    # '小优没法控制离线的空调呀，先去看看设备联网情况吧。
    offline = ["备联网了吗", "先去看看设备联网情况吧", "小优没法控制离线的"]
    for line in offline:
        if line in res['response']:
            sign = 1

    # 'response': '只有在智家APP添加了你的海尔空调，小优才能帮你，快去添加吧。
    # 你好像还没有在智家APP绑定它们，绑定之后小优就能帮你啦。
    # ù你还没有绑定海尔热水器，先去智家App添加一个吧
    # 可我没有找到客厅的冰箱呀……
    # 客厅里有冰箱吗？是不是因为还没绑定，所以小优才找不到它？'
    #ù小优连接不上这台设备，它还好吗？/ù检查一下吧
    no_devices = ["没有找到","还没绑定","只有在智家APP添加了", "快去添加吧", "绑定之后小优就能帮你啦", "你好像还没有在智家APP绑定它们", "你还没有绑定", "先去智家App添加一个吧","小优连接不上这台设备"]
    for no_device in no_devices:
        if no_device in res['response']:
            sign = 2
    if "没有" in res['response'] and "找到" in res['response']:
        sign=2

    # 'response': '设备的当前状态，无法执行该命令。
    # 判断是否状态冲突
    # ù设备的当前状态，无法执行该命令
    error_status = ["设备的当前状态，无法执行该命令"]
    for error_statu in error_status:
        if error_statu in res['response']:
            sign = 3

    # 设备没有开机
    # 小优发现你的洗衣机还没有开机呢
    #关着呢
    offs = ["还没有开机呢","关着呢"]
    for off in offs:
        if off in res['response']:
            sign = 4

    # 设备好像没有这个功能哦，换个说法，再召唤我一次吧
    nofunctions = ["设备好像没有这个功能"]
    for nofunction in nofunctions:
        if nofunction in res['response']:
            sign=5

    #{'response': '你的海尔账号信息过期了，用智家APP重新登录一下吧', 'retCode': 'I00001-00008', 'retInfo': 'accessToken不合法

    nosigns=["账号信息过期","重新登录一下"]
    for nosign in nosigns:
        if nosign in res['response']:
            sign=6

    # #可我没有找到客厅的冰箱呀……
    # #客厅里有冰箱吗？是不是因为还没绑定，所以小优才找不到它？'
    # no_finds=["没有找到"]
    # for no_find in no_finds:
    #     if no_find in res['response']:
    #         sign=7

    # print("=========================")
    # print(res['response'])
    # print(res['retInfo'])
    # print(res['response'])
    # time.sleep(10)

    # if res['retInfo']=="accessToken不合法":
    #     print("======================================")
    #     print("账号登录失败，重新登录")

    if sign==0:
        flag, fail_reasons, res, sign=judeg_res_sucess(baseres,res)
    else:
        flag, fail_reasons, res, sign=judeg_res_error(baseres,res,sign)

    return flag, fail_reasons, res, sign
    # if sign == 1:
    #     flag = True
    #     fail_reasons.insert(0, "设备离线了")
    #     logging.error("设备离线了")
    # if sign == 2:
    #     flag = True
    #     fail_reasons.insert(0, "没有添加设备")
    #     logging.error("还没有添加设备")
    #
    # if sign == 3:
    #     flag = True
    #     fail_reasons.insert(0, "状态冲突")
    #     logging.error("状态发生冲突")
    #
    # if sign == 4:
    #     flag = True
    #     fail_reasons.insert(0, "设备没有开机")
    #     logging.error("设备没有开机")
    # if sign==5:
    #     flag=True
    #     fail_reasons.insert(0,"设备无此功能")
    #     logging.error("设备无此功能")


def judeg_res_sucess(baseres,res):
    #结果比较，传入的数据是一条用例和请求返回的字典
    # logging.info("比较用例和返回的数据")
    # logging.info("传入的用例是：")
    # logging.info(baseres)
    # logging.info("传入的请求返回是： ")
    # logging.info(res)

    fail_reasons=[]
    flag=True


    try:
    #校验status_code
        logging.info("status_code")
        if res['status_code']==str(200):
            logging.info("status_code=200，正确")
        else:
            temp_txt = 'status_code不是200。'
            logging.error(temp_txt)
            fail_reasons.append(temp_txt)
            flag = False
    except:
        temp_txt = 'status_code对比异常'
        logging.error(temp_txt)
        fail_reasons.append(temp_txt)
        flag = False


    #校验retCode==00000
    try:
        logging.info("校验retCode")
        if res['retCode']=='00000':
            logging.info("retCode正确")
        elif res['retCode']=='I00004-00004':
            temp_txt='retCode返回I00004-00004。'
            logging.error(temp_txt)
            fail_reasons.append(temp_txt)
        else:
            temp_txt = 'retCode返回错误'
            logging.error(temp_txt)
            fail_reasons.append(temp_txt)
            flag=False
    except:
        temp_txt = 'retCode对比异常'
        logging.error(temp_txt)
        fail_reasons.append(temp_txt)
        flag = False


    logging.info("对比category")
    try:
        if baseres['category']==None:
            logging.warning("baseres['category']为空，略过")
        else:
            if baseres['category']==res['category']:
                logging.info("category对比正确")
            else:
                temp_txt=" category参数不正确，失败 。"
                logging.error(temp_txt)
                fail_reasons.append(temp_txt)
                flag=False
    except:
        temp_txt = " category对比异常"
        logging.error(temp_txt)
        fail_reasons.append(temp_txt)
        flag = False


    try:
        logging.info("对比domain")
        if baseres['domain']==None:
            logging.warning("domain参数为空，略过")
        else:
            if baseres['domain']==res['domain']:
                logging.info("domain参数正确")
            else:
                temp_txt="domain不正确，失败。"
                fail_reasons.append(temp_txt)
                flag=False
    except:
        temp_txt = "domain对比异常"
        fail_reasons.append(temp_txt)
        flag = False

    try:

        logging.info("对比action")
        if baseres['action']==None:
            logging.warning("action参数为空，略过")
        else:
            if baseres['action']==res['action']:
                logging.info("action参数正确")
            else:
                temp_txt='action参数不正确，失败。'
                fail_reasons.append(temp_txt)
                flag=False
    except:
        logging.error("action对比失败")
        temp_txt = 'action对比失败'
        fail_reasons.append(temp_txt)
        flag = False

    try:
        logging.info('expect_response参数校验')
        if baseres['expect_response']==None:
            logging.warning("expect_response参数为空，略过")
        else:
            expect_res=baseres['expect_response']
            #print(expect_res)
            #print(type(expect_res))
            expect_responses=re.split('[,;、，]',expect_res)
            #print(expect_responses)
            res_response=res['response']
            #print(res_response)
            for expect_response in expect_responses:

                if "|" in expect_response:
                    expect_flag=False
                    expect_tmps=re.split('\|',expect_response)
                    for expect_tmp in expect_tmps:
                        if expect_tmp in res_response:
                            expect_flag=True
                    if expect_flag==False:
                        tmp = "expect_response中的 " + expect_response + " 校验失败"
                        logging.error(tmp)
                        fail_reasons.append(tmp)
                        flag = False


                elif expect_response in res_response:
                    logging.info(expect_response+" 校验正确 ")
                else:
                    tmp="expect_response中的 "+expect_response+" 校验失败"
                    logging.error(tmp)
                    fail_reasons.append(tmp)
                    flag=False
    except:
        tmp = "expect_response校验异常 "
        logging.error(tmp)
        fail_reasons.append(tmp)
        flag = False

    try:
        logging.info("expect_results开始校验")
        if baseres['expect_results']==None:
            logging.warning("expect_results参数为空，略过")
        else:
            expect_results={}
            expect_results_key=[]
            expect_res=baseres['expect_results']
            print(expect_res)
            print(type(expect_res))
            expect_results_tmp=re.split('[,，、]',expect_res)
            print(expect_results_tmp)
            for i in expect_results_tmp:

                i_tmp=re.split('=',i)
                print(i_tmp)
                expect_results[i_tmp[0]]=i_tmp[1]
                expect_results_key.append(i_tmp[0])
            print(expect_results)
            print(expect_results_key)

            logging.info("expect_results参数格式化后的内容")
            logging.info(expect_results)
            for key in expect_results_key:
                if str(expect_results[key]) in str(res[key]) or str(expect_results[key])=="x":
                    logging.info("expect_results中的 "+key+" 校验正确")
                else:
                    logging.error("expect_results中的 " + key + " 校验失败")
                    tmp="expect_results中的 " + key + " 校验失败"
                    # print(expect_results[key])
                    # print(type(expect_results[key]))
                    # print(res[key])
                    # print(type(res[key]))

                    fail_reasons.append(tmp)
                    flag=False
    except:
        tmp = "expect_results校验异常 "

        fail_reasons.append(tmp)
        flag = False

    sign=0

#     #离线情况
#     #'小优没法控制离线的空调呀，先去看看设备联网情况吧。
#     offline=["备联网了吗","先去看看设备联网情况吧","小优没法控制离线的"]
#     for line in offline:
#         if line in res['response']:
#             sign=1
#
#     # if sign==1:
#     #     flag=True
#     #     fail_reasons.insert(0,"设备离线了")
#     #     logging.error("设备离线了")
#
#     # 'response': '只有在智家APP添加了你的海尔空调，小优才能帮你，快去添加吧。
#     #你好像还没有在智家APP绑定它们，绑定之后小优就能帮你啦。
#     #ù你还没有绑定海尔热水器，先去智家App添加一个吧
#     no_devices=["只有在智家APP添加了","快去添加吧","绑定之后小优就能帮你啦","你好像还没有在智家APP绑定它们","你还没有绑定","先去智家App添加一个吧"]
#     for no_device in no_devices:
#         if no_device in res['response']:
#             sign=2
#     # if sign==2:
#     #     flag=True
#     #     fail_reasons.insert(0,"没有添加设备")
#     #     logging.error("还没有添加设备")
#
#     # 'response': '设备的当前状态，无法执行该命令。
#     #判断是否状态冲突
#     #ù设备的当前状态，无法执行该命令
#     error_status=["设备的当前状态，无法执行该命令"]
#     for error_statu in error_status:
#         if error_statu in res['response']:
#             sign=3
#
#     #设备没有开机
#     #小优发现你的洗衣机还没有开机呢
#     offs=["还没有开机呢"]
#     for off in offs:
#         if off in res['response']:
#             sign=4
#
# #设备好像没有这个功能哦，换个说法，再召唤我一次吧
#     nofunctions=["设备好像没有这个功能"]
#     for nofunction in nofunctions:
#         if nofunction in res['response']
#
#
#     if sign==1:
#         flag=True
#         fail_reasons.insert(0,"设备离线了")
#         logging.error("设备离线了")
#     if sign==2:
#         flag=True
#         fail_reasons.insert(0,"没有添加设备")
#         logging.error("还没有添加设备")
#
#     if sign==3:
#         flag=True
#         fail_reasons.insert(0,"状态冲突")
#         logging.error("状态发生冲突")
#
#     if sign==4:
#         flag=True
#         fail_reasons.insert(0,"设备没有开机")
#         logging.error("设备没有开机")


    #返回flag,fail_reasons,res
    return flag,fail_reasons,res,sign


        






if __name__=="__main__":
    res={'city': '青岛市', 'nlpUuid': '', 'domain': 'weather', 'action': 'query', 'location': '青岛', 'type': '天气', 'category': 'weather', 'params_action': 'query', 'response': '/ù青岛今天天气中度雾霾转多云，-3度到4度，/ù平均温度比昨天低1度，东北风4级，/ù空气质量指数197，中度污染。有大风蓝色预警，/ù请注意防范', 'retCode': '00000', 'retStatus': 0, 'sync_tts': ''}
    # print(res)
    # print(type(res))

    baseres={'id': 1, 'name': '天气查询', 'engine': 'x20', 'nlpVersion': 'jar.1.6.62-model.1.6.62-2020111801', 'query': '青岛天气怎么样', 'retCode': None, 'category': 'weather', 'domain': 'weather', 'action': 'query', 'isDialog': 'F', 'expect_response': '青岛,今天，天气、度、平均温度比昨天、空气质量指数、污染', 'expect_results': 'city=青岛市，action=query、location=青岛', 'sync_tts': None, 'IsPass': None, 'failReason': None, 'real_result': None}
    # print(baseres)
    # print(type(baseres))

    flag,fail_reasons,res=judeg_res(baseres,res)
    print("================")
    print(flag)
    print(fail_reasons)
    print(res)