import json
from datetime import datetime
import time
import sys
import os
import requests
import json
f_path=os.path.dirname(__file__)
print(f_path)
from requests.exceptions import ConnectTimeout

ff_path=os.path.dirname(f_path)
nlp_excel_path=os.path.join(ff_path,'dataNew')
nlp_result_path=os.path.join(ff_path,'nlpNew_result')

#url="http://ai.haier.net:11000/access/ai-access/nlp?engine=x20&needcontent=yes"


import logging
import logging.config
CON_LOG='log.conf'
logging.config.fileConfig(CON_LOG)
logging=logging.getLogger()

def Merge(dict1, dict2):
#字典合并方法
    logging.info("合并字典")
    res = {**dict1, **dict2}
    return res

def get_config(name,file=None):
    #获取发送请求的参数
    if file==None:
        file="request.config"
    with open(file,'r') as f:
        lines=f.readlines()
        #print(lines)
        for line in lines:
            line=line.strip('\n')
            config_name=line.split('=')[0]
            config_value=line.split('=')[1]
            if config_name==name:
                config_value=str(config_value)
                config_value.strip('\n')
                print(config_value)
                return config_value
            # print(config_name)
            # print(config_value)


def send_url(query,file_config=None,url=None):
    logging.info("开发发送语音接口请求")
    logging.info("发送的指令是: "+str(query))

    if url==None:
        url="http://ai.haier.net:11000/access/ai-access/nlp?engine=x20&needcontent=yes"
    headers = {"Accept": "*/*", "User-Agent": "Mozilla/4.0"}
    headers["Content-Type"] = "application/json;charset=utf-8"
    headers["appid"] = get_config('appid',file_config)
    headers["appVersion"] = get_config('appVersion',file_config)
    headers["clientid"] = get_config('clientid',file_config)
    headers["accessToken"] = get_config('accessToken',file_config)
    headers["sequenceId"] = get_config('sequenceId',file_config)
    headers["sign"] = get_config('sign',file_config)
    headers["timestamp"] = str(datetime.now().strftime('%Y%m%d%H%M%S'))
    headers["language"] = "zh-cn"
    headers["timezone"] = str(8)
    headers["familyId"] = get_config('familyId',file_config)
    headers["userId"] = get_config('userId',file_config)
    headers["wakeupStat"] = get_config('wakeupStat',file_config)
    # headers["sn"]="20201126172210179000187288"
    body_json = {}
    body_json["query"] = query
    body_jsons = json.dumps(body_json)
    logging.info("请求参数")
    logging.info("url = "+str(url))
    logging.info("headers = "+str(headers))
    logging.info("data = "+str(body_jsons))
    try:
        res = requests.post(url=url, headers=headers, data=body_jsons)
    except:
        logging.error("请求出现了异常")
        res=None
        return res
    else:
        logging.info("请求返回的数据是： ")
        logging.info(str(res.text))
        # print(res.text)
        #print(res.elapsed.microseconds/1000)
        return res
    # print(res)
    # print(res.text)


def handle_response(response):
    logging.info("开始处理返回的数据")
    res={}

    # print(response)
    # print(type(response))

    if response==None:
        #print(type(res))
        logging.error("请求返回失败")
        return res
    else:
        myjson=response.json()
        logging.info("返回的数据转成json格式: ")
        logging.info(myjson)
        print(myjson)

        #
        # print(myjson['data']['nlpResult'])
        # print(type(myjson['data']['nlpResult']))

        try:
            result_dev=myjson['data']['nlpResult']['results'][0]['dev']
        except:
            result_dev={}
            logging.error("result_dev获取异常")
        else:
            logging.info("获取result_dev参数")
            logging.info(result_dev)
            res=Merge(res,result_dev)

        try:
            result_params = myjson['data']['nlpResult']['results'][0]['params']
        except:
            logging.error("result_params获取异常")
            result_params={}
        else:
            logging.info("获取result_params")
            logging.info(result_params)
            res=Merge(res,result_params)


        try:
            category=myjson['data']['nlpResult']['category']
        except:
            logging.error("category参数获取失败")
            category=''
        else:
            logging.info("获取category参数")
            logging.info(category)
            res['category']=category

        try:
            domain=myjson['data']['nlpResult']['domain']
        except:
            logging.error("domain参数获取失败")
            domain=''
        else:
            logging.info("获取domain参数")
            logging.info(domain)
            res['domain']=domain

        try:
            dev_nickName=myjson['data']['nlpResult']['results'][0]['dev']['nickName']
        except:
            logging.error("获取dev_nickName参数失败")
            dev_nickName=''
        else:
            logging.info("获取dev_nickName参数: ")
            logging.info(dev_nickName)
            res['dev_nickName']=dev_nickName

        try:
            dev_name=myjson['data']['nlpResult']['results'][0]['dev']['name']
        except:
            logging.info("获取dev_name参数失败")
            dev_name=''
        else:
            logging.info("获取dev_name参数")
            logging.info(dev_name)
            res['dev_name']=dev_name

        try:
            dev_type=myjson['data']['nlpResult']['results'][0]['dev']['type']
        except:
            dev_type=''
        else:
            res['dev_type']=dev_type

        try:
            params_action=myjson['data']['nlpResult']['results'][0]['params']['action']
        except:
            logging.error("params_action参数获取失败")
            params_action=''
        else:
            logging.info("获取params_action")
            logging.info(params_action)
            res['params_action']=params_action

        try:
            _response=myjson['response']
        except:
            _response=''
        else:
            res['response']=_response

        try:
            retCode=myjson['retCode']
        except:
            retCode=''
        else:
            res['retCode']=retCode

        print(res)
        print(type(res))




'''   
def data_connect():
    headers = {"Accept": "*/*", "User-Agent": "Mozilla/4.0"}
    headers["Content-Type"] = "application/json;charset=utf-8"
    headers["appid"] = "MB-SDOT20-0000"
    headers["appVersion"] = "2.5.37"
    headers["clientid"] = "ACB1EE302412"
    #headers["accessToken"] = "TGT1WZ2XKV2QM2OI27GEA9LJWCDWM0"
    #headers["accessToken"] = "TGT1WZ2XKV2QM2OI27GEA9LJWCDWM0"
    headers["accessToken"] = "TGT3PJ2PKGE5ZDKY2UUWMRIUI9DEK0"
    #headers["token"]= "TGT1WZ2XKV2QM2OI27GEA9LJWCDWM0"
    #headers["clientid"] = "HARDWARE_VOICE04FA83724014"
    # headers["accessToken"] = "TGTITDQ7KCOEPWR26C9UXFI0K8G500"
    headers["sequenceId"] = "08002700DC94-15110519074300001"
    headers["sign"] = "fbd962ab1aa1c745eebf9b0c60c5c42f"
    #headers["is-test"]='1ewerqerqer'
    headers["timestamp"] = str(datetime.now().strftime('%Y%m%d%H%M%S'))
    headers["language"] = "zh-cn"
    headers["timezone"] = str(8)
    # headers["deviceId"]="ACB1EE26DF1D"
    # headers["deviceId"] = "36427446" deviceid要改成userid,不携带此参数
    #headers["deviceId"] = "36427446"
    # headers["deviceId"]="0007A8944FB5"
    headers["familyId"] = "640162750021000001"
    headers["userId"]="3642744"
    headers["wakeupStat"]="yes"
    #headers["sn"]="20201126172210179000187288"
    body_json = {}
    body_json["query"]="青岛的天气怎么样"
    body_jsons = json.dumps(body_json)

    #commonMethods.http_post(nlpurl, headers, body_jsons)
    print(url)
    res=requests.post(url=url,headers=headers,data=body_jsons)
    print(res)
    print(res.text)
'''

if __name__=="__main__":
    #file_config='request.config'

    url = "http://ai.haier.net:11000/access/ai-access/nlp?engine=x20&needcontent=yes"
    response=send_url(query="天气怎么样")
    handle_response(response)
    #data_connect()
    # get_config("x")