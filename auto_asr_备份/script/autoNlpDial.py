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
nlp_excel_path=os.path.join(ff_path,'dataDial')
nlp_result_path=os.path.join(ff_path,'nlpDial_result')
# url="http://203.130.41.37:11000/access/ai-access/nlp?"
# url="http://ai.haier.net:11000/access/ai-access/nlp?"
# url="http://ai.haier.net:11000/yanzheng/ai-access/nlp?"
# url="http://47.93.125.250:22000/ai-access/nlp?"
env = sys.argv[1]
url="http://ai.haier.net:11000/"+env+"/ai-access/nlp?"
# url="http://52.172.29.124:11000/ai-access/nlp?"
def data_connect(sheet, row, clo_num):
    headers = {"Accept": "*/*", "User-Agent": "Mozilla/4.0"}
    headers["Content-Type"] = "application/json;charset=utf-8"
    headers["appid"] = "MB-SDOT20-0000"
    headers["appVersion"] = "2.0.1"
    headers["clientid"] = "C8631420A431"
    headers["accessToken"] = "TGTLB5Q0U7QNAMJ2F0L3S30XWVBK00"
    # headers["clientid"] = "7947FBE8-CB01-4056-B26A-4A34A3B6B65D"
    # headers["accessToken"] = "TGT1V3Z666GSX4461YU1YHQDYT7JM0"
    headers["sequenceId"]="08002700DC94-15110519074300001"
    headers["sign"] = "bd4495183b97e8133aeab2f1916fed41"
    headers["timestamp"] = str(datetime.now().strftime('%Y%m%d%H%M%S'))
    headers["language"]="zh-cn"
    headers["timezone"]=8
    # headers["deviceId"]="ACB1EE26DF1D"
    headers["deviceId"]="ABCDE"
    # headers["deviceId"]="0007A8944FB5"
    headers["familyId"] = "256116551160000001"
    body_json = {}
    value = sheet.cell(row, 4).value
    key = sheet.cell(0, 4).value
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
    expect_retcode = sheet.cell(row, clo_num - 8).value
    expect_category=sheet.cell(row, clo_num - 7).value
    expect_domain=sheet.cell(row, clo_num - 6).value
    expect_domain_list=expect_domain.split('|')
    expect_action=sheet.cell(row, clo_num - 5).value
    expect_action_list=expect_action.split('|')
    checkDialog = sheet.cell(row, clo_num - 4).value
    expect_response=sheet.cell(row, clo_num - 3).value
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
    if isinstance(expect_retcode, float):
        expect_retcode = str(int(expect_retcode))
    dict={}
    if (res_datas is not None)and('data' in res_datas)and(res_datas['data'] is not None)and(bool(res_datas['data'])):
        if('nlpResult' in res_datas['data']):
            category = res_datas['data']['nlpResult'].get("category")
            domain = res_datas['data']['nlpResult'].get("domain")
            isDialog = res_datas['data']['nlpResult'].get("isDialog")
            results = res_datas['data']['nlpResult'].get("results")
        params={}
        if len(results) > 0:
            params = results[0]['params']
            if ('action' in params):
                action = params["action"]
            if ('intentList' in params):
                intentList = params['intentList']
                action = intentList[0].get('action')
        paramsStr=json.dumps(params,ensure_ascii=False)
        print (paramsStr)
        domainIndex = expect_domain_list.index(domain) if (domain in expect_domain_list) else -1
        actionIndex = expect_action_list.index(action) if (action in expect_action_list) else -1
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
        elif ((str(expect_retcode) == str(retcode)) or (str(expect_retcode) == "")) and responseFlag  and (
                (category == expect_category) or (expect_category == "")) and (
                (domainIndex>=0) or (expect_domain == "")) and (
                (actionIndex>=0) or (expect_action == ""))and((expect_action_list[domainIndex]==action)or expect_action==""or(expect_domain_list[actionIndex]==domain)):
                flag = "成功"
                print ("第%d条测试用例测试通过" % row)
        else:
            print ("第%d条测试用例测试失败" % row)
    elif (res_datas is not None)and(str(expect_retcode) == str(retcode)):
        flag = "成功"
        print ("第%d条测试用例测试通过" % row)
    else:
        print ("第%d条测试用例测试失败" % row)

    flag_dict[row] = flag
    if domain is None:
        domain=""
    if action is None:
        action=""
    response = "category:" + category + ";domain:" + domain + ";action:" + action + ";" + response + ";sn:" + sn
    result_dict[row] = response

if __name__ == '__main__':
    exit = 0
    files = os.listdir(nlp_excel_path)
    for file in files:
        flag_dict = {}
        result_dict = {}
        sheet, clo_num, row_num = commonMethods.read_testdata(nlp_excel_path, file)
        for row in range(1, row_num):
            data_connect(sheet, row, clo_num)
            time.sleep(1)
        isExit=commonMethods.write_result(flag_dict, result_dict, nlp_excel_path, file, nlp_result_path,exit)
        exit=exit+isExit
    if exit == 0:
        sys.exit(0)
    else:
        sys.exit(1)