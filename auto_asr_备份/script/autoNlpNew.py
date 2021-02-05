# -*- coding: utf-8 -*-

import json
from datetime import datetime
import time
import commonMethods
import sys
import os
# reload(sys)
# sys.setdefaultencoding( "utf-8" )
f_path=os.path.dirname(__file__)
ff_path=os.path.dirname(f_path)
nlp_excel_path=os.path.join(ff_path,'dataNew')
nlp_result_path=os.path.join(ff_path,'nlpNew_result')
env = sys.argv[1]
url="http://ai.haier.net:11000/"+env+"/ai-access/nlp?"
# url="http://47.93.125.250:22000/ai-access/nlp?"
def data_connect(sheet, row, clo_num):
    headers = {"Accept": "*/*", "User-Agent": "Mozilla/4.0"}
    headers["Content-Type"] = "application/json;charset=utf-8"
    headers["appid"] = "MB-SDOT20-0000"
    headers["appVersion"] = "2.0.1"
    headers["clientid"] = "FADE2F239AF05FC9EFC130E112B521B0"
    headers["accessToken"] = "82628866659949a8a3e142ad6f031a79"
    # headers["clientid"] = "HARDWARE_VOICE04FA83724014"
    # headers["accessToken"] = "TGTITDQ7KCOEPWR26C9UXFI0K8G500"
    headers["sequenceId"]="08002700DC94-15110519074300001"
    headers["sign"] = "bd4495183b97e8133aeab2f1916fed41"
    headers["timestamp"] = str(datetime.now().strftime('%Y%m%d%H%M%S'))
    headers["language"]="zh-cn"
    headers["timezone"]=8
    # headers["deviceId"]="ACB1EE26DF1D"
    headers["deviceId"]="ABC00000011"
    # headers["deviceId"]="0007A8944FB5"
    headers["familyId"] = "256116551160000001"
    body_json = {}
    value = str(sheet.cell(row, 4).value)
    key = str(sheet.cell(0, 4).value)
    if not value == "":
        body_json[str(key)] = str(value)
    body_jsons = json.dumps(body_json)
    print ("request_data" + body_jsons.encode('utf8').decode('unicode_escape'))
    engine = sheet.cell(row, 2).value
    if engine=="haierTV":
        headers["deviceId"] = "MAGICMIRRORABC"
    addurl=""
    if not engine=="":
        addurl="engine="+engine+"&"
    needcontent = sheet.cell(row, 3).value
    if not needcontent == "":
        addurl = addurl + "needcontent=" + needcontent + "&"
    nlpurl=url+addurl
    print ("request_url:", nlpurl)
    res_data, res_code = commonMethods.http_post(nlpurl, headers, body_jsons)
    expect_retcode = sheet.cell(row, 5).value
    expect_category=sheet.cell(row, 6).value
    expect_domain=sheet.cell(row, 7).value
    expect_domain_list=expect_domain.split('|')
    expect_action=sheet.cell(row, 8).value
    expect_action_list=expect_action.split('|')
    action_flag="or"
    if "&" in expect_action:
        action_flag = "and"
        expect_action_list=expect_action.split('&')
    checkDialog = sheet.cell(row, clo_num - 5).value
    expect_response=str(sheet.cell(row, clo_num - 4).value)
    expect_response_flag='|'
    expect_response_list = expect_response.split('|')
    if '&' in expect_response:
        expect_response_list = expect_response.split('&')
        expect_response_flag='&'
    res_datas = None
    retcode = None
    category=""
    domain=""
    isDialog=""
    results=""
    action = ""
    response=""
    sn=""
    nlpVersion=""
    if commonMethods.is_json(res_data):
        res_datas = json.loads(res_data)
        retcode = res_datas.get("retCode")
        response = res_datas['response']
        response = response.replace('/ù', '')
        if response is None:
            response="null"
        sn=res_datas.get("sn")
        # if ('data' in res_datas)&(len(res_datas['data'])>0):
        #     results = res_datas['data']['nlpResult'].get("results")
        #     if(len(results)>0):
        #         mode = results[0].get('params').get('mode')
    flag = "失败"
    flag_reason = ""
    if isinstance(expect_retcode, float):
        expect_retcode = str(int(expect_retcode))
    dict={}
    if (res_datas is not None)and('data' in res_datas)and(res_datas['data'] is not None)and(bool(res_datas['data'])):
        if('nlpResult' in res_datas['data']):
            category = res_datas['data']['nlpResult'].get("category")
            domain = res_datas['data']['nlpResult'].get("domain")
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
        print("actionList: "+str(actionList))
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
        if (str(checkDialog) is not "F") and (isDialog is True):
            flag = "成功"
            print ("第%d条测试用例测试通过" % row)
        # action_flag = False
        # if action_flag is "and" and action_list == expect_action_list:
        #     action_flag = True
        else:
            flag, flag_reason = commonMethods.isError(expect_retcode, retcode, responseFlag,
                                                      category, expect_category, expect_domain,
                                                      expect_action, action,actionList, domain)
        if flag == "成功":
            print(file + " 第%d条测试用例测试通过" % row)
        else:
            print(file + " 第%d条测试用例测试失败" % row)
            exit = False
    # elif (res_datas is not None)and(str(expect_retcode) == str(retcode)):
    #     flag = "成功"
    #     print ("第%d条测试用例测试通过" % row)
    else:
        print ("第%d条测试用例测试失败" % row)

    flag_dict[row] = flag
    if domain is None:
        domain=""
    if action is None:
        action=""
    response = "category:" + category + ";domain:" + domain + ";action:" + action + ";" + response + ";sn:" + sn
    result_dict[row] = response
    flag_reason_dict[row]=flag_reason
    print(flag_reason)
    nlp_version[row]=nlpVersion

if __name__ == '__main__':
    exit = 0
    files = os.listdir(nlp_excel_path)
    for file in files:
        flag_dict = {}
        result_dict = {}
        flag_reason_dict={}
        nlp_version={}
        sheet, clo_num, row_num = commonMethods.read_testdata(nlp_excel_path, file)
        for row in range(1, row_num):
            data_connect(sheet, row, clo_num)
        isExit=commonMethods.write_result_time(flag_dict, result_dict, flag_reason_dict, nlp_version, nlp_excel_path, file, nlp_result_path, exit)
        exit=exit+isExit
    if exit == 0:
        sys.exit(0)
    else:
        sys.exit(1)