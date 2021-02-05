# -*- coding: utf-8 -*-

import json
import traceback
from datetime import datetime
import time
import commonMethods
import sys
import os
# reload(sys)
# sys.setdefaultencoding( "utf-8" )
f_path=os.path.dirname(__file__)
ff_path=os.path.dirname(f_path)
nlp_excel_path=os.path.join(ff_path,'dataNlp')
nlp_result_path=os.path.join(ff_path,'nlp_result')
# url="http://203.130.41.37:11000/access/ai-access/nlp?"
# url="http://ai.haier.net:11000/access/ai-access/nlp?"
# url="http://ai.haier.net:11000/yanzheng/ai-access/nlp?"
# url="http://221.122.92.15:11000/ai-access/nlp?"
env = sys.argv[1]
url="http://ai.haier.net:11000/"+env+"/ai-access/nlp?"
def data_connect(sheet, row, clo_num):
    headers = {"Accept": "*/*", "User-Agent": "Mozilla/4.0"}
    headers["Content-Type"] = "application/json;charset=utf-8"
    headers["appid"] = "MB-SDOT20-0000"
    headers["appVersion"] = "2.3.10"
    headers["clientid"] = "FADE2F239AF05FC9EFC130E112B521B0"
    headers["accessToken"] = "82628866659949a8a3e142ad6f031a79"
    headers["sequenceId"]="08002700DC94-15110519074300001"
    headers["sign"] = "bd4495183b97e8133aeab2f1916fed41"
    headers["timestamp"] = str(datetime.now().strftime('%Y%m%d%H%M%S'))
    headers["language"]="zh-cn"
    headers["timezone"]=8
    # headers["deviceId"]="C8631420007B"
    headers["deviceId"] = "C86314227C33"
    # headers["appKey"] = 'bf0dacd18e5abc73a452374b9ce3287d'
    # headers["sdkVer"] = "1.0"
    body_json = {}
    value = sheet.cell(row, 5).value
    key = sheet.cell(0, 5).value
    if not value == "":
        body_json[str(key)] = str(value)
    body_jsons = json.dumps(body_json)
    print ("request_data" + body_jsons.encode('utf8').decode('unicode_escape'))
    engine = sheet.cell(row, 2).value
    addurl=""
    needcontent = sheet.cell(row, 3).value
    if not needcontent == "":
        addurl = addurl + "needcontent=" + needcontent + "&"
    if not engine=="":
        addurl=addurl+"engine="+engine+"&"
    nlpurl=url+addurl
    print ("request_url:", nlpurl)
    res_data, res_code = commonMethods.http_post(nlpurl, headers, body_jsons)
    expect_retcode = sheet.cell(row, clo_num - 7).value
    expect_category=sheet.cell(row, clo_num - 6).value
    expect_domain=sheet.cell(row, clo_num - 5).value
    expect_action = sheet.cell(row, clo_num - 4).value
    expect_response=sheet.cell(row, clo_num - 3).value
    checkDialog=sheet.cell(row, 4).value
    res_datas = None
    retcode = None
    category=""
    domain=""
    action=""
    response=""
    sn=""
    if commonMethods.is_json(res_data):
        res_datas = json.loads(res_data)
        retcode = res_datas.get("retCode")
        response = res_datas['response']
        if response is None:
            response="null"
        response = response.replace('/ù', '')
        sn=res_datas.get("sn")
    flag = "失败"
    if isinstance(expect_retcode, float):
        expect_retcode = str(int(expect_retcode))
    dict={}
    if (res_datas is not None)and('data' in res_datas) and (res_datas['data'] is not None)and (len(res_datas['data']) > 0):
        category = res_datas['data']['nlpResult'].get("category")
        domain = res_datas['data']['nlpResult'].get("domain")
        results = res_datas['data']['nlpResult'].get("results")
        isDialog = res_datas['data']['nlpResult'].get("isDialog")
        params={}
        if len(results) > 0:
            params = results[0]['params']
            if ('action' in params):
                action = params["action"]
            if ('intentList' in params):
                intentList = params['intentList']
                action = intentList[0].get('action')
        paramsStr=json.dumps(params,ensure_ascii=False)
        print(paramsStr)
        if (str(checkDialog) is not "F") and isDialog is True:
            flag = "成功"
            print(file + " 第%d条测试用例测试通过" % row)
        elif ((str(expect_retcode) == str(retcode)) or (str(expect_retcode) == "")) and ((
                expect_response in response)or(expect_response in paramsStr)) and (
                (category == expect_category) or (expect_category == "")) and (
                (domain == expect_domain) or (expect_domain == "")) and (
                (action == expect_action) or (expect_action == "")):
            flag = "成功"
            print ("第%d条测试用例测试通过" % row)
        else:
            print ("第%d条测试用例测试失败" % row)
    elif (res_datas is not None)and((str(expect_retcode) == str(retcode))):
        flag = "成功"
        print ("第%d条测试用例测试通过" % row)
    else:
        print ("第%d条测试用例测试失败" % row)

    flag_dict[row] = flag
    if category is None:
        category=""
    if domain is None:
        domain=""
    if action is None:
        action=""
    response = "category:" + category + ";domain:" + domain + ";action:"+action +","+ response + ";sn:" + sn
    result_dict[row]  = response

if __name__ == '__main__':
    exit = 0
    files = os.listdir(nlp_excel_path)
    for file in files:
        flag_dict = {}
        result_dict = {}
        sheet, clo_num, row_num = commonMethods.read_testdata(nlp_excel_path,file)
        for row in range(1, row_num):
                data_connect(sheet, row, clo_num)
        isExit=commonMethods.write_result(flag_dict, result_dict, nlp_excel_path, file, nlp_result_path,exit)
        exit=exit+isExit
    if exit == 0:
        sys.exit(0)
    else:
        sys.exit(1)