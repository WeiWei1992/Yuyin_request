# -*- coding: utf-8 -*-

import json
from datetime import datetime
import time

import asyncio

import commonMethods
import sys
import os
import logging
# reload(sys)
# sys.setdefaultencoding( "utf-8" )
f_path=os.path.dirname(__file__)
ff_path=os.path.dirname(f_path)
nlp_excel_path=os.path.join(ff_path,'dataNlpBase')
nlp_result_path=os.path.join(ff_path,'nlpBase_result')
# url="http://203.130.41.37:11000/access/ai-access/nlp?"
# url="http://ai.haier.net:11000/access/ai-access/nlp?"
# url="http://ai.haier.net:11000/yanzheng/ai-access/nlp?"
# url="http://221.122.92.15:11000/ai-access/nlp?"
exit=True
env=sys.argv[1]
url="http://ai.haier.net:11000/"+env+"/ai-access/nlp?"
async def data_connect(sheet, row, clo_num,file,headers):
    global exit
    body_json = {}
    for clo in range(7, (clo_num - 6)):
        value = sheet.cell(row, clo).value
        key = sheet.cell(0, clo).value
        if not value == "":
            body_json[str(key)] = str(value)
    body_jsons = json.dumps(body_json)
    print ("request_data" + body_jsons.encode('utf8').decode('unicode_escape'))
    engine = sheet.cell(row, 2).value
    addurl=""
    if not engine=="":
        addurl="engine="+engine+"&"
    needcontent=sheet.cell(row,3).value
    if not needcontent=="":
        addurl=addurl+"needcontent="+needcontent+"&"
    opmode=sheet.cell(row,4).value
    if not opmode=="":
        addurl=addurl+"opmode="+opmode+"&"
    syncmode=sheet.cell(row,5).value
    if not syncmode=="":
        addurl=addurl+"syncmode="+syncmode+"&"
    ttssplit=sheet.cell(row,6).value
    if not ttssplit=="":
        addurl=addurl+"ttssplit="+ttssplit
    nlpurl=url+addurl
    print ("request_url:", nlpurl)
    res_data =await commonMethods.aiohttp_post(nlpurl, headers, body_jsons)
    expect_retcode = sheet.cell(row, clo_num - 6).value
    expect_category=sheet.cell(row, clo_num - 5).value
    expect_domain=sheet.cell(row, clo_num - 4).value
    expect_response=sheet.cell(row, clo_num - 3).value
    res_datas = None
    retcode = None
    category=""
    domain=""
    response=""
    sn=""
    if commonMethods.is_json(res_data):
        res_datas = json.loads(res_data)
        retcode = res_datas.get("retCode")
        response = res_datas['response']
        sn=res_datas.get("sn")
    flag = "失败"
    if isinstance(expect_retcode, float):
        expect_retcode = str(int(expect_retcode))
    dict={}
    if (res_datas is not None)and('data' in res_datas) and (res_datas['data'] is not None)and(len(res_datas['data']) > 0):
        category = res_datas['data']['nlpResult'].get("category")
        domain = res_datas['data']['nlpResult'].get("domain")
        if (str(retcode) == '00000') and (expect_response in response) and (
                (category == expect_category) or (expect_category == "")) and (
                (domain == expect_domain) or (expect_domain == "")):
            flag = "成功"
            print ("第%d条测试用例测试通过" % row)
        else:
            exit = False
            print ("第%d条测试用例测试失败" % row)
    else:
        exit = False
        print ("第%d条测试用例测试失败" % row)
    response = "category:" + category + ";domain:" + domain + ";" + response + ";sn:" + sn
    return flag, response
async def fileTraverse(files,num):
    flag_dict={}
    result_dict={}
    flag_reason_dict={}
    file=files[num]
    sheet, clo_num, row_num = commonMethods.read_testdata(nlp_excel_path, files[num])
    headers = {"Accept": "*/*", "User-Agent": "Mozilla/4.0"}
    headers["Content-Type"] = "application/json;charset=utf-8"
    headers["appid"] = "MB-SDOT20-0000"
    headers["appVersion"] = "2.3.10"
    headers["sequenceId"]="08002700DC94-15110519074300001"
    headers["clientid"] = "482FAF1E-F16A-4335-AB41-8A3637017CA3"
    headers["accessToken"] = "TGT1AI4PD637HAPA2G9885J0YJ89C0"
    headers["sign"] = "bd4495183b97e8133aeab2f1916fed41"
    headers["timestamp"] = str(datetime.now().strftime('%Y%m%d%H%M%S'))
    headers["language"]="zh-cn"
    headers["timezone"]='8'
    headers["deviceId"] = "C86314200327"
    if ("知识库1" in file):
        headers["deviceId"] = "ABECD1"
    elif "知识库2" in file:
        headers["deviceId"]="ABCDE2"
    elif "知识库3" in file:
        headers["deviceId"]="ABCDE3"
    elif "知识库4" in file:
        headers["deviceId"]="ABCDE4"
    else:
        headers["deviceId"]="C86314206569"
    for row in range(1, row_num):
        flag,response=await data_connect(sheet, row, clo_num,file[0:-6],headers)
        flag_dict[row]=flag
        result_dict[row]=response
        # flag_reason_dict[row]=flag_reason
    isExit=commonMethods.write_result1(flag_dict, result_dict, flag_reason_dict,nlp_excel_path, file, nlp_result_path,exit)

if __name__ == '__main__':
    # exit = 0
    loop = asyncio.get_event_loop()
    files = os.listdir(nlp_excel_path)
    # files.sort(key=lambda x: int(x[-6]))
    task = []
    for i in range(len(files)):
        task.append(fileTraverse(files, i))
    loop.run_until_complete(asyncio.gather(*task))
    try:
        commonMethods.write_error_result(nlp_result_path)
    except Exception as e:
        logging.exception(e)
        print ("错误case写入失败")
    else:
        print ("错误case已写入errorResult文件")
    if exit is True:
        sys.exit(0)
    else:
        sys.exit(1)
    # files = os.listdir(nlp_excel_path)
    # for file in files:
    #     flag_dict = {}
    #     result_dict = {}
    #     sheet, clo_num, row_num = commonMethods.read_testdata(nlp_excel_path,file)
    #     for row in range(1, row_num):
    #         data_connect(sheet, row, clo_num)
    #     isExit=commonMethods.write_result(flag_dict, result_dict,nlp_excel_path,file,nlp_result_path,exit)
    #     exit=exit+isExit
    # if exit==0:
    #     sys.exit(0)
    # else:
    #     sys.exit(1)