# -*- coding: utf-8 -*-

import base64
import json
import os
from datetime import datetime
import sys
import commonMethods
import wave
import chardet
# reload(sys)
# sys.setdefaultencoding('utf8')
# asr_url="http://120.27.157.19:11000/ai-access/asr?engine=xunfei&nlpmodel=asrtest"
f_path=os.path.dirname(__file__)
ff_path=os.path.dirname(f_path)
excel_path=os.path.join(ff_path,'dataAsr')
result_path=os.path.join(ff_path,'asr_result')
dir_path=os.path.join(ff_path,"audio")
asr_url="http://ai.haier.net:11000/yanzheng/ai-access/asr?engine=xunfei&opmode=none&ttssplit=yes&needcontent=yes&syncmode=yes"
# asr_url="http://ai.haier.net:11000/new/ai-access/asr?engine=xunfei&nlpmodel=x20"


# 读取音频文件
audio_files = os.listdir(dir_path)
audio_files.sort(key=lambda x:x[-5])
def read_audio_name():
    audoiNameList=[]
    audoiFileList=[]
    for i in audio_files:
        audoiNameList.append(i[:-4])
        audoiFileList.append(i)
    print(audoiNameList)
    print(audoiFileList)

def read_asr_data(audioName):
    file_path=os.path.join(dir_path,audioName)
    # file_path=os.path.join(dir_path,audio_files[1])
    with open (file_path,mode='rb') as pcmf:
        if not pcmf is None:
            data = pcmf.read()
            if str(data[0:4]) == "RIFF":
                print("data has RIFF")
                data = data[44:]
    return data

# json拼接，断言
def data_connect(sheet,row,clo_num):
    audioName=sheet.cell(row,2).value
    audiodata=read_asr_data(audioName)
    str_audio=str(base64.b64encode(audiodata),encoding='utf-8')
    headers = {"Accept": "*/*", "User-Agent": "Mozilla/4.0"}
    headers["Content-Type"] = "application/json;charset=utf-8"
    headers["appKey"] = 'bf0dacd18e5abc73a452374b9ce3287d'
    headers["clientid"] = "B20666D6E8565AC94E0F1085735D5555"
    headers["appVersion"] = "2.0.12"
    headers["appid"] = "MB-SDOT20-0000"
    headers["accessToken"] = "TGT2WKLNCGDW6R982VCTD0H82TB2T0"
    headers["sign"] = "cfbba45f7cadda393d6a2068bbcd29cd"
    headers["timestamp"]=str(datetime.now().strftime('%Y%m%d%H%M%S'))
    headers["sdkVer"]="1.0"
    body_json = {}
    body_json["speechLang"] = "zh-CN"
    body_json["speechFormat"] = "wav"
    body_json["speechRate"] = 16000
    body_json["speechch"] = 1
    body_json["duid"] = "C89346404BAB"
    body_json["rawLen"] = len(audiodata)
    body_json["recogmode"] = "once"
    body_json["opmode"] = "remote"
    body_json["speech"] = str_audio
    ## 讯飞： x20
    body_json["nlpmodel"] = "X20"
    nlpmodel=sheet.cell(row,1).value
    asr_url1=asr_url+"&nlpmodel="+nlpmodel
    body_jsons=json.dumps(body_json)
    # print ("request_data"+body_jsons)
    res_data=None
    print(asr_url1)
    print(audioName)
    res_data, res_code=commonMethods.http_post(asr_url1,headers,body_jsons)
    expect_text=sheet.cell(row,3).value
    expect_text_list=expect_text.split('|')
    # expect_retcode=sheet.cell(row,clo_num-3).value
    data=None
    text=""
    sn=""
    text_dict={}
    text_list1=None
    text_list2=None
    if commonMethods.is_json(res_data):
        data = json.loads(res_data)
    if not data is None:
        text_list1 = data.get("data")
        sn=data.get("sn")
    if not text_list1 is None:
        text_list2 = text_list1.get("asrResult")
    if not text_list2 is None:
        text_dict = text_list2[0]
    if not text_dict is None:
        text = text_dict.get("recogniationText")
    retcode=None
    if not data is None:
        retcode = data.get("retCode")
    flag="失败"
    # if isinstance(expect_retcode,float):
    #     expect_retcode=str(int(expect_retcode))
    if  text in expect_text_list:
        flag="成功"
        print ("第%d条测试用例测试通过"%row)
    elif (expect_text==""):
        flag = "成功"
        print ("第%d条测试用例测试通过" % row)
    else:
        print ("第%d条测试用例测试失败"%row)
    result=text+";sn:"+sn
    flag_dict[row]=flag
    result_dict[row]=result

if __name__ == '__main__':
    # read_audio_name()
    exit = 0
    files = os.listdir(excel_path)
    for file in files:
        flag_dict = {}
        result_dict = {}
        sheet, clo_num, row_num = commonMethods.read_testdata(excel_path, file)
        for row in range(1, row_num):
            data_connect(sheet, row, clo_num)
        isExit = commonMethods.write_result(flag_dict, result_dict, excel_path, file, result_path, exit)
        exit = exit + isExit
    if exit == 0:
        sys.exit(0)
    else:
        sys.exit(1)