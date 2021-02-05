# -*- coding: utf-8 -*-
import asyncio
import json
from datetime import datetime
import time
import commonMethods
import sys
import os
import logging
# reload(sys)
# sys.setdefaultencoding( "utf-8" )
f_path=os.path.dirname(__file__)
ff_path=os.path.dirname(f_path)
nlp_excel_path=os.path.join(ff_path,'dataNlpDevice')
nlp_result_path=os.path.join(ff_path,'nlpDevice_result')
# url="http://203.130.41.37:11000/access/ai-access/nlp?"
# url="http://ai.haier.net:11000/access/ai-access/nlp?"
# url="http://ai.haier.net:11000/yanzheng/ai-access/nlp?"

env = sys.argv[1]
url="http://ai.haier.net:11000/"+env+"/ai-access/nlp?"
# 验收环境
# url="http://47.93.125.250:22000/ai-access/nlp?"


exit=True
async def data_connect(sheet, row, clo_num,file,headers):
    body_json = {}
    global exit
    value = sheet.cell(row, 4).value
    key = sheet.cell(0, 4).value
    if not value == "":
        body_json[str(key)] = str(value)
    body_jsons = json.dumps(body_json)
    print (file+(" 第%d条测试用例" % row)+"request_data" + body_jsons.encode('utf8').decode('unicode_escape'))
    engine = sheet.cell(row, 2).value
    addurl=""
    if not engine=="":
        addurl="engine="+engine+"&"
    addurl = addurl + "needcontent=yes"
    nlpurl=url+addurl
    print ("request_url:", nlpurl)
    # time_start=time.time()
    # print(time_start)
    res_data = await commonMethods.aiohttp_post(nlpurl, headers, body_jsons)
    # time_end=time.time()
    # time_all=int((time_end-time_start)*1000)
    # print(time_end,time_all)
    expect_retcode = sheet.cell(row, clo_num - 9).value
    expect_category=sheet.cell(row, clo_num - 8).value
    expect_domain=sheet.cell(row, clo_num - 7).value
    # expect_domain_list=expect_domain.split('|')
    expect_action=sheet.cell(row, clo_num - 6).value
    # expect_action_list=expect_action.split('|')
    checkDialog=sheet.cell(row,clo_num-5).value
    expect_response=str(sheet.cell(row, clo_num - 4).value)
    expect_response_flag = '|'
    expect_response_list = expect_response.split('|')
    if '&' in expect_response:
        expect_response_list = expect_response.split('&')
        expect_response_flag = '&'
    res_datas = None
    retcode = None
    category=""
    domain=""
    action = ""
    response=""
    sn=""
    nlpVersion = ''
    if commonMethods.is_json(res_data):
        res_datas = json.loads(res_data)
        retcode = res_datas.get("retCode")
        response = res_datas['response']
        if response is None:
            response="null"
        response = response.replace('/ù', '')
        sn=res_datas.get("sn")
    flag = "失败"
    flag_reason=""
    if isinstance(expect_retcode, float):
        expect_retcode = str(int(expect_retcode))
    dict={}
    if (res_datas is not None)and('data' in res_datas)and(res_datas['data'] is not None)and(bool(res_datas['data'])):
        category = res_datas['data']['nlpResult'].get("category")
        domain = res_datas['data']['nlpResult'].get("domain")
        isDialog = res_datas['data']['nlpResult'].get("isDialog")
        results = res_datas['data']['nlpResult'].get("results")
        nlpResult=res_datas['data']['nlpResult']
        if 'nlpVersion' in nlpResult.keys():
            nlpVersion=nlpResult.get('nlpVersion')
        params={}
        actionList = []
        if len(results) > 0:
            params = results[0]['params']
            if ('action' in params):
                action = params["action"]
            if ('intentList' in params):
                intentList = params['intentList']
                action = intentList[0].get('action')
                for i in range(len(intentList)):
                    actionList.append(intentList[i].get('action'))
        paramsStr=json.dumps(params,ensure_ascii=False)
        print (paramsStr)
        responseFlag = False
        responseFlag1=0
        if expect_response_flag=='&':
            for i in range(len(expect_response_list)):
                if expect_response_list[i] not in response and expect_response_list[i] not in paramsStr:
                    responseFlag1 += 1
        if responseFlag1==0:
            responseFlag=True
        if expect_response_flag == '|':
            responseFlag = False
            for i in range(len(expect_response_list)):
                if expect_response_list[i]  in response or expect_response_list[i]  in paramsStr:
                    responseFlag = True
        if(str(checkDialog) is not "F") and (isDialog is True):
            flag = "成功"
            print (file+" 第%d条测试用例测试通过" % row)
        else:
            flag, flag_reason = commonMethods.isError(expect_retcode, retcode, responseFlag,
                                                      category, expect_category, expect_domain,
                                                      expect_action, action,actionList, domain)
        if flag == "成功":
            print(file + " 第%d条测试用例测试通过" % row)
        else:
            print (file+" 第%d条测试用例测试失败" % row)
            exit=False
    # elif (res_datas is not None)and(str(expect_retcode) == str(retcode)):
    #     flag = "成功"
    #     print (file+" 第%d条测试用例测试通过" % row)
    else:
        flag_reason = "返回结果异常"
        print (file+" 第%d条测试用例测试失败" % row)
        exit=False
    # flag_dict[row] = flag
    if domain is None:
        domain=""
    if action is None:
        action=""
    response = "category:" + category + ";domain:" + domain + ";action:" + action + ";" + response + ";sn:" + sn
    # result_dict[row] = response
    return flag,response,flag_reason,nlpVersion

async def fileTraverse(files,num):
    flag_dict={}
    result_dict={}
    time_dict={}
    flag_reason_dict={}
    nlp_version={}
    file=files[num]
    sheet, clo_num, row_num = commonMethods.read_testdata(nlp_excel_path, files[num])
    headers = {"Accept": "*/*", "User-Agent": "Mozilla/4.0"}
    headers["Content-Type"] = "application/json;charset=utf-8"
    headers["appid"] = "MB-SDOT20-0000"
    headers["appVersion"] = "2.3.10"
    headers["sequenceId"]="08002700DC94-15110519074300001"
    headers["clientid"] = "9A0B4B4ADA67B2962B57AD132602C3DF"
    headers["accessToken"] = "e685cce0a60a4d60a759152aeed76874"
    # headers["clientid"] = "ACB1EE26DF1F"
    # headers["accessToken"] = "TGT2NL8832093UEA2RRHJUT0CXDLV0"
    headers["sign"] = "bd4495183b97e8133aeab2f1916fed41"
    headers["timestamp"] = str(datetime.now().strftime('%Y%m%d%H%M%S'))
    headers["language"]="zh-cn"
    headers["timezone"]='8'
    headers["deviceId"] = "C86314200327"
    # headers["familyId"] = "256116551160000001"
    # if ("设备控制1" in file):
    #     headers["deviceId"] = "C86314200327"
    # elif "设备控制2" in file:
    #     headers["deviceId"]="ACB1EE30240B"
    # elif "技能" in file:
    #     headers["deviceId"]="C86314209A9D"
    # elif "冰箱" in file:
    #     headers["deviceId"]="DC330D239ECC"
    # elif "滚筒" in file:
    #     headers["deviceId"]="04FA83E456F5"
    # elif "洗衣机" in file:
    #     headers["deviceId"]="04FA83E456F5"
    # elif "电视" in file:
    #     headers["deviceId"]="MAGICMIRRORABC"
    # else:
    #     headers["deviceId"]="C86314206569"
    if ("设备控制1" in file):
        headers["deviceId"] = "ABC00001"
    elif "设备控制2" in file:
        headers["deviceId"]="ABC00002"
    elif "设备控制3" in file:
        headers["deviceId"]="ABC00009"
    elif "技能相关1" in file:
        headers["deviceId"]="ABC00003"
    elif "技能相关2" in file:
        headers["deviceId"]="ABC00008"
    elif "冰箱" in file:
        headers["deviceId"]="ABC00004"
    elif "滚筒" in file:
        headers["deviceId"]="ABC00005"
    elif "洗衣机" in file:
        headers["deviceId"]="ABC00006"
    elif "电视" in file:
        headers["deviceId"]="MAGICMIRRORABC"
    else:
        headers["deviceId"]="ABC00007"
    for row in range(1, row_num):
        flag,response,flag_reason,nlpVersion=await data_connect(sheet, row, clo_num,file[0:-5],headers)
        flag_dict[row]=flag
        result_dict[row]=response
        # time_dict[row]=time_all
        flag_reason_dict[row]=flag_reason
        print(nlpVersion)
        nlp_version[row]=nlpVersion
    isExit=commonMethods.write_result_time(flag_dict, result_dict, flag_reason_dict,nlp_version,nlp_excel_path, file, nlp_result_path,exit)
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    files = os.listdir(nlp_excel_path)
    # files.sort(key=lambda x:int(x[-6]))
    if env=="yanzheng":
        if "食材管理生产.xlsx" in files:
            files.remove("食材管理生产.xlsx")
    if env=="access":
        if "食材管理验证.xlsx" in files:
            files.remove("食材管理验证.xlsx")
    task=[]
    for i in range(len(files)):
        task.append(fileTraverse(files,i))
    loop.run_until_complete(asyncio.gather(*task))
    try:
        commonMethods.write_error_result1(nlp_result_path)
    except Exception as e:
        logging.exception(e)
        print ("错误case写入失败")
    else:
        print ("错误case已写入errorResult文件")
    if exit is True:
        sys.exit(0)
    else:
        sys.exit(1)