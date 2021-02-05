import base64
import json
import os
from datetime import datetime
import sys

import requests

f_path=os.path.dirname(__file__)
print(f_path)
ff_path=os.path.dirname(f_path)
print(ff_path)
excel_path=os.path.join(ff_path,'dataAsr')
print(excel_path)
result_path=os.path.join(ff_path,'asr_result')
print(result_path)
dir_path=os.path.join(ff_path,'audio')
print(dir_path)

asr_url="http://ai.haier.net:11000/yanzheng/ai-access/asr?engine=xunfei&opmode=none&ttssplit=yes&needcontent=yes&syncmode=yes"

#读取音频文件
audio_files=os.listdir(dir_path)
print(audio_files)
audio_files.sort(key=lambda x:x[-5])
print(audio_files)
def read_audio_name():
    audoiNameList=[]
    audoiFileList=[]
    for i in audio_files:
        audoiNameList.append(i[:-4])
        audoiFileList.append(i)
    print(audoiNameList)
    print(audoiFileList)


#wav格式转成二进制
def read_asr_data(audioName):
    file_path=os.path.join(dir_path,audioName)
    # file_path=os.path.join(dir_path,audio_files[1])
    with open (file_path,mode='rb') as pcmf:
        if not pcmf is None:
            data = pcmf.read()
            # print("xxxxx")
            # print(data)
            if str(data[0:4]) == "RIFF":
                print("data has RIFF")
                data = data[44:]
    return data

def ToBase64(audioName):
    file_path = os.path.join(dir_path, audioName)
    with open(file_path,'rb') as fileObj:
        audio_data=fileObj.read()
        base64_data=base64.b64encode(audio_data)
    return base64_data

def data_connect(audioName):
    audiodata=read_asr_data(audioName)
    print(len((audiodata)))
    str_audio=str(base64.b64encode(audiodata),encoding='utf-8')
    # print(len(str_audio))
    #
    str_audio1=ToBase64(audioName)
    # print(len(str_audio1))
    headers = {"Accept": "*/*", "User-Agent": "Mozilla/4.0"}
    headers["Content-Type"] = "application/json;charset=utf-8"
    headers["appKey"]='a361aa3546e108f0c24cf9936896ba8c'

    #headers["clientid"] = "B20666D6E8565AC94E0F1085735D5555"
    headers["clientid"]="ACB1EE302412"

    headers["appVersion"] = "2.5.37"
    headers["appid"] = "MB-SDOT20-0000"
    headers["accessToken"] = "TGT1WZ2XKV2QM2OI27GEA9LJWCDWM0"

    headers["sign"] = "da907af02bbaf9d493fd537fd6bfe858"
    headers["timestamp"] = str(datetime.now().strftime('%Y%m%d%H%M%S'))
    headers["sdkVer"] = "1.11.2"
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
    # nlpmodel = sheet.cell(row, 1).value
    asr_url1 = asr_url + "&nlpmodel=" + "x20"
    body_jsons = json.dumps(body_json)
    # print ("request_data"+body_jsons)
    res_data = None
    print(asr_url1)
    print(audioName)

    res=requests.post(url=asr_url,headers=headers,data=body_jsons)
    print(res)
    print(res.text)

if __name__=="__main__":
    # read_audio_name()
    audioName="5点.wav"
    # data=read_asr_data(audioName)
    # print(data)
    # data_base64=str(base64.b64encode(data),encoding='utf-8')
    # print(data_base64)
    # data2=ToBase64(audioName)
    # print(data2)
    data_connect(audioName)
