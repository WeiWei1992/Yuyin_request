# -*- coding: utf-8 -*-
import base64
import json
import os
from datetime import datetime
import commonMethods
import sys
# reload(sys)
# sys.setdefaultencoding( "utf-8" )
sys.path.append('../site-packages')
# tts_excel_path="D:/git/autoYun/auto_asr/dataTts"
# url="http://120.27.157.19:11000/ai-access/tts?engine="
# url="http://ai.haier.net:11000/yanzheng/ai-access/tts?engine="
url="http://ai.haier.net:11000/new/ai-access/tts?engine="
# tts_result_path="../tts_result"
f_path=os.path.dirname(__file__)
ff_path=os.path.dirname(f_path)
tts_excel_path=os.path.join(ff_path,'dataTts')
tts_result_path=os.path.join(ff_path,'tts_result')
# file_path = sys.path('../') + "/audio_data/"+str(datetime.now().strftime('%Y%m%d%H%M%S'))+"/"
# path_exist=os.path.exists(file_path)
# if not path_exist:
#     os.mkdir(file_path)
def data_connect(sheet,row,clo_num):
    headers = {"Accept": "*/*", "User-Agent": "Mozilla/4.0"}
    headers["Content-Type"] = "application/json;charset=utf-8"
    headers["appKey"] = 'bf0dacd18e5abc73a452374b9ce3287d'
    headers["clientid"] = "2759B15E6DF3EAC379DFF872F55664E6"
    headers["appVersion"] = "2.0.1"
    headers["appid"] = "MB-SDOT20-0000"
    headers["accessToken"] = "TGTCCYWOMZ1DSX42FTZYFDUL4KWX00"
    headers["sign"] = "bd4495183b97e8133aeab2f1916fed41"
    # headers["isnlp"] = "0"
    # headers["nlpmodel"] = "xunfei"
    # headers["opmode"] = "xunfei"
    # headers["needcontent"] = "false"
    headers["timestamp"]=str(datetime.now().strftime('%Y%m%d%H%M%S'))
    headers["sdkVer"]="1.0"
    # headers["deviceId"]="C89346404BAB"
    body_json = {}
    for clo in range(3,(clo_num-3)):
        value=sheet.cell(row,clo).value
        key=sheet.cell(0,clo).value
        if not value=="":
            if isinstance(value,str):
                body_json[str(key)] = str(value)
            if isinstance(value,float):
                if value%1==0:
                    body_json[str(key)] = int(value)
                else:
                    body_json[str(key)]=value
            if key=="text":
                body_json[str(key)] = str(value)+str(datetime.now().strftime('%Y%m%d%H%M%S'))

    body_jsons=json.dumps(body_json)
    print ("request_data"+body_jsons)
    engine = sheet.cell(row, 2).value
    tts_url=url+str(engine)
    print ("request_url:",tts_url)
    res_data, res_code=commonMethods.http_post(tts_url,headers,body_jsons)
    expect_retcode=sheet.cell(row,clo_num-3).value
    res_datas=None
    retcode=None
    retInfo=""
    sn=""
    if commonMethods.is_json(res_data):
        res_datas = json.loads(res_data)
        retcode = res_datas.get("retCode")
        retInfo=res_datas.get("retInfo")
        sn=res_datas.get("sn")
    flag="失败"
    if isinstance(expect_retcode,float):
        expect_retcode=str(int(expect_retcode))
    if(retcode is not None):
        print ("expect_retcode:" + expect_retcode + "  retcode:" + retcode)
        if (str(retcode) != '00000') and (str(expect_retcode) == str(retcode)):
            flag = "成功"
            print ("第%d条测试用例测试通过" % row)
        elif (str(retcode) == '00000') and(res_datas['data'] is not None) and (str(expect_retcode) == str(retcode)):
            flag = "成功"
            print ("第%d条测试用例测试通过" % row)
        else:
            print ("第%d条测试用例测试失败" % row)
    else:
        print ("第%d条测试用例测试失败"% row)
    # if (str(retcode)=='00000')&(res_datas['data'] is not None):
        # with open(file_path + str(row) + "."+res_datas['data']['format'], 'wb') as f:
        #     f.write(base64.b64decode(res_datas['data']['speech']))
        #     print "语音文件已生成"
    if retcode is None:
        retcode=""
    res_data="res_data:"+retcode+";retInfo:"+retInfo+";sn:"+sn
    flag_dict[row]=flag
    result_dict[row]=res_data

if __name__ == '__main__':
    exit = 0
    files = os.listdir(tts_excel_path)
    for file in files:
        flag_dict = {}
        result_dict = {}
        sheet, clo_num, row_num = commonMethods.read_testdata(tts_excel_path,file)
        print (sheet,clo_num,row_num)
        for row in range(1, row_num):
            data_connect(sheet, row, clo_num)
        isExit=commonMethods.write_result(flag_dict, result_dict, tts_excel_path, file, tts_result_path,exit)
        exit=exit+isExit
    if exit == 0:
        sys.exit(0)
    else:
        sys.exit(1)