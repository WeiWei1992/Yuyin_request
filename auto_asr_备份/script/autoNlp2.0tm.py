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
nlp_excel_path=os.path.join(ff_path,'dataNlp2.0tm')
nlp_result_path=os.path.join(ff_path,'resultNlp2.0tm')
# env = sys.argv[1]
# 验收
# url1="http://47.93.125.250:22000/ai-access/nlp?engine="
# 联调
# url1="http://182.92.163.135:22000/ai-access/nlp?engine="
url1="http://aiapi-lt.haiersmarthomes.com:11000/ai-access/nlp?engine="


# url1 = "http://ai.haier.net:11000/yanzheng/ai-access/nlp?engine="
url2="&needcontent=yes&neednlp=yes&needSplit=true"
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
    addurl=url1+engine+url2
    print ("request_url:", addurl)
    print(headers)
    res_data = await commonMethods.aiohttp_post(addurl, headers, body_jsons)
    expect_retcode = sheet.cell(row, 5).value
    expect_category=sheet.cell(row, 6).value
    expect_domain=sheet.cell(row, 7).value
    expect_action=sheet.cell(row, 8).value
    checkDialog=sheet.cell(row,9).value
    expect_response = str(sheet.cell(row, clo_num - 4).value)
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
        if domain is None:
            domain=="None"
        isDialog = res_datas['data']['nlpResult'].get("isDialog")
        results = res_datas['data']['nlpResult'].get("results")
        nlpResult = res_datas['data']['nlpResult']
        if 'nlpVersion' in nlpResult.keys():
            nlpVersion = nlpResult.get('nlpVersion')
        params={}
        actionList = []
        if len(results) > 0:
            params = results[0]['params']
            if ('action' in params):
                action = params["action"]
            if ('intentList' in params):
                intentList = params['intentList']
                action = intentList[0].get('action')
                len_intentlist=len(intentList)
                for i in range(len_intentlist):
                    actionList.append(intentList[i].get('action'))
        if action is None:
            action="None"
        paramsStr=json.dumps(params,ensure_ascii=False)
        print (paramsStr)
        responseFlag=False
        responseFlag1 = 0
        if expect_response_flag == '&':
            for i in range(len(expect_response_list)):
                if expect_response_list[i] not in response and expect_response_list[i] not in paramsStr:
                    responseFlag1 += 1
        if responseFlag1 == 0:
            responseFlag = True
        if expect_response_flag == '|':
            responseFlag = False
            for i in range(len(expect_response_list)):
                print(expect_response_list[i])
                if expect_response_list[i] in response or expect_response_list[i] in paramsStr:
                    responseFlag = True
        if(str(checkDialog) is not "F") and (isDialog is True):
            flag = "成功"
            print (file+" 第%d条测试用例测试通过" % row)
        else:
            flag, flag_reason = commonMethods.isError(expect_retcode, retcode, responseFlag,
                                                      category, expect_category, expect_domain,
                                                       expect_action, action,actionList,  domain)
            if flag == "成功":
                print(file + " 第%d条测试用例测试通过" % row)
            else:
                print(file + " 第%d条测试用例测试失败" % row)
                exit = False
    else:
        flag_reason="返回结果异常"
        print (file+" 第%d条测试用例测试失败" % row)
        exit=False
    # flag_dict[row] = flag
    response = "category:" + category + ";domain:" + domain + ";action:" + action + ";" + response + ";sn:" + sn
    # result_dict[row] = response
    return flag,response,flag_reason,nlpVersion

async def fileTraverse(files,num):
    flag_dict={}
    result_dict={}
    flag_reason_dict={}
    nlp_version_dict={}
    file=files[num]
    sheet, clo_num, row_num = commonMethods.read_testdata(nlp_excel_path, files[num])
    headers = {"Accept": "*/*", "User-Agent": "Mozilla/4.0"}
    headers["Content-Type"] = "application/json;charset=utf-8"
    headers["appVersion"] = "0.2.8"
    headers["appid"] = "MB-SAC-0000"
    headers["clientid"] = "FF930C564359A70D325C6539E7E570EC"
    headers["accessToken"] = "TGT12JUAB7Q113FZ2CTS32HJCH1Z10"
    headers["sequenceId"]="08002700DC94-15110519074300001"
    headers["sign"] = "bd4495183b97e8133aeab2f1916fed41"
    headers["timestamp"] = str(datetime.now().strftime('%Y%m%d%H%M%S'))
    headers["language"]="zh-cn"
    headers["timezone"]='8'
    headers["deviceId"]=commonMethods.findDevice(file)
    headers["familyId"] = "256116551160000001"
    for row in range(1, row_num):
        flag,response,flag_reason,nlpVersion=await data_connect(sheet, row, clo_num,file[0:-5],headers)
        flag_dict[row]=flag
        result_dict[row]=response
        flag_reason_dict[row]=flag_reason
        nlp_version_dict[row]=nlpVersion
    isExit=commonMethods.write_result2(flag_dict, result_dict, flag_reason_dict,nlp_excel_path, file, nlp_result_path,exit,nlp_version_dict)
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    files = os.listdir(nlp_excel_path)
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