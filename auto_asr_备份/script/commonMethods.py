# -*- coding: utf-8 -*-
import json
import os
import time
import urllib
from datetime import datetime
from urllib import parse,request
import sys
import xlwt
from xlutils.copy import copy
import xlrd
from xlwt import Workbook
import importlib
# import chardet
import logging
import configparser
from aiohttp import ClientSession
import asyncio
importlib.reload(sys)
sys.path.append('D:/git/autoYun/auto_asr/site-packages')
f_path=os.path.dirname(__file__)
# ff_path=os.path.dirname(f_path)
cf=configparser.ConfigParser()
path=os.path.join(f_path,"config.txt")
cf.read(path,encoding='utf-8')
# 判断是否是json格式数据
def is_json(myjson):
    if myjson is None:
        return False
    try:
        # json_string=json.dumps(myjson)
        json_object=json.loads(myjson)
    except ValueError as e:
        return False
    return True

# 发送http请求
def http_post(url,headers,data):
    res_header={}
    req=request.Request(url,data=data.encode(encoding='UTF8'),headers=headers)
    # request=urllib2.Request(url,data,headers)
    response=None
    res_data=None
    fails = 0
    while True:
        try:
            if fails < 3:
                response = urllib.request.urlopen(req, data=None,timeout=10)
                res_data = response.read()
                if is_json(res_data):
                    print ("response_data", str(res_data,encoding='utf8'))
                    res_code = response.getcode()
                    print  (res_code)
                    break
                else:
                    print ("异常response_data", res_data)
                    print("异常重试")
                    fails=fails+1
                    res_code = -1
            else:
                break
        except Exception as e:
            logging.exception(e)
            fails = fails + 1
            print ("异常重试")
            if hasattr(e, 'reason'):
                print ('Reason:', e.reason)
                res_code = -1
            if hasattr(e, 'code'):
                res_code = e.code
            else:
                res_code = -1
    if response:
        response.close()
    return res_data,res_code

async def aiohttp_post(url,headersData,data):
    res_data=None
    fails = 0
    # req=request.Request(url,data=data.encode(encoding='UTF8'),headers=headers
    while True:
                async with ClientSession() as session:
                    try:
                        async with session.post(url, data=data, headers=headersData) as response:
                            res_data = await response.text()
                            print(data.encode('utf8').decode('unicode_escape')," ; ","response_data",res_data)
                    except:
                        print("异常重试1")
                if fails<3:
                    if is_json(res_data):
                        res_datas=json.loads(res_data)
                        # break
                        if ('data' in res_datas) and(res_datas['data']is not None) and (len(res_datas['data'])>0):
                            break
                        else:
                            print("超时重试")
                            fails = fails + 1
                    else:
                        print(res_data)
                        print("异常重试2")
                        fails = fails + 1
                else:
                    break
    return res_data

# 读取测试数据
def read_testdata(excel_path,file):
    file_path=os.path.join(excel_path,file)
    wb=xlrd.open_workbook(filename=file_path)
    sheet=wb.sheet_by_index(0)
    clo_num=sheet.ncols
    row_num=sheet.nrows
    return sheet,clo_num,row_num

# 将结果写入execl表
def write_result(flag_dict,result_dict,excel_path,file,result_path,exit):
    file_path = os.path.join(excel_path, file)
    rb = xlrd.open_workbook(filename=file_path)
    global sheetGlobal
    sheetGlobal= rb.sheet_by_index(0)
    clo_num = sheetGlobal.ncols
    wb = copy(rb)
    sheet = wb.get_sheet(0)
    red_style = xlwt.easyxf("font:colour_index red;")
    green_style = xlwt.easyxf("font:colour_index green;")
    allCase=len(flag_dict)
    failCase=0
    for row in flag_dict:
        flag = str(flag_dict[row])
        if flag == '成功':
            sheet.write(row, clo_num - 2, flag, green_style)
        if flag == '失败':
            exit = 1
            sheet.write(row, clo_num - 2, flag, red_style)
            failCase=failCase+1
    for row in result_dict:
        result = str(result_dict[row])
        if (len(result) <= 32767):
            sheet.write(row, clo_num - 1, result)
    name = file[:len(file)-5] + str(datetime.now().strftime('%Y%m%d%H%M%S')) + "result.xls"
    result_paths = os.path.join(result_path, name)
    wb.save(result_paths)
    rate = float(allCase - failCase) / float(allCase)
    rate = '%.2f%%' % (rate * 100.0)
    # file=file.decode('gb2312').encode('utf-8')
    log = "#"+file[:len(file)-5] + "   总case数:" + str(allCase) + "   成功case数:" + str(
        (allCase - failCase)) + "   失败case数:" + str(failCase) + "   成功率:" + str(rate)
    print (log)
    print ("大功告成！")
    return exit

def write_result2(flag_dict,result_dict,flag_reason_dict,excel_path,file,result_path,exit,nlp_version_dict={}):
    file_path = os.path.join(excel_path, file)
    rb = xlrd.open_workbook(filename=file_path)
    global sheetGlobal
    sheetGlobal= rb.sheet_by_index(0)
    clo_num = sheetGlobal.ncols
    row_num = sheetGlobal.nrows
    domainList=[]
    wb = copy(rb)
    sheet = wb.get_sheet(0)
    for i in range(1,row_num):
        domain=sheetGlobal.cell(i,7).value
        domainList.append(domain)
    domainListSin = list(set(domainList))
    print(domainListSin)
    for domain in domainListSin:
        if ("|" in domain) or ("&" in domain):
            domainListSin.remove(domain)
    print(domainListSin)
    for domain in domainListSin:
        successCase=0
        failcase=0
        for row in range(1,len(flag_dict)+1):
            if sheetGlobal.cell(row,7).value == domain:
                if str(flag_dict[row]) == "成功":
                    successCase=successCase+1
                else:
                    failcase=failcase+1
        allcase=successCase+failcase
        try:
            fileName = cf.get("domainSet", domain)
        except:
            fileName=domain
        if (len(fileName) < 12):
            fileName += " " * 2 * (12 - len(fileName))
        allcase = str(allcase)
        if len(allcase) < 6:
            allcase += " " * (6 - len(allcase))
        successCase = str(successCase)
        if len(successCase) < 6:
            successCase += " " * (6 - len(successCase))
        failcase = str(failcase)
        if len(failcase) < 6:
            failcase += " " * (6 - len(failcase))
        rate = float(successCase) / float(allcase)
        rate = '%.2f%%' % (rate * 100.0)
        log = "#" + fileName + " 总case数:" + allcase + "   成功case数:" + successCase + "   失败case数:" + failcase + "   成功率:" + str(
            rate)
        print(log)
    red_style = xlwt.easyxf("font:colour_index red;")
    green_style = xlwt.easyxf("font:colour_index green;")
    allCase=len(flag_dict)
    failCase=0
    for row in flag_dict:
        flag = str(flag_dict[row])
        if flag == '成功':
            sheet.write(row, clo_num - 3, flag, green_style)
        if flag == '失败':
            exit = 1
            sheet.write(row, clo_num - 3, flag, red_style)
            failCase=failCase+1
    for row in result_dict:
        result = str(result_dict[row])
        if (len(result) <= 32767):
            sheet.write(row, clo_num - 1, result)
    for row in flag_reason_dict:
        flag_reason=flag_reason_dict[row]
        sheet.write(row,clo_num-2,flag_reason)
    if not  nlp_version_dict is {}:
        for row in nlp_version_dict:
            nlpVersion = nlp_version_dict[row]
            sheet.write(row, 3, nlpVersion)
    name = file[:len(file)-5] + str(datetime.now().strftime('%Y%m%d%H%M%S')) + "result.xls"
    result_paths = os.path.join(result_path, name)
    wb.save(result_paths)
    print ("大功告成！")
    return exit

def write_result1(flag_dict,result_dict,flag_reason_dict,excel_path,file,result_path,exit,nlp_version_dict={}):
    file_path = os.path.join(excel_path, file)
    rb = xlrd.open_workbook(filename=file_path)
    global sheetGlobal
    sheetGlobal= rb.sheet_by_index(0)
    clo_num = sheetGlobal.ncols
    wb = copy(rb)
    sheet = wb.get_sheet(0)
    red_style = xlwt.easyxf("font:colour_index red;")
    green_style = xlwt.easyxf("font:colour_index green;")
    allCase=len(flag_dict)
    failCase=0
    for row in flag_dict:
        flag = str(flag_dict[row])
        if flag == '成功':
            sheet.write(row, clo_num - 3, flag, green_style)
        if flag == '失败':
            exit = 1
            sheet.write(row, clo_num - 3, flag, red_style)
            failCase=failCase+1
    for row in result_dict:
        result = str(result_dict[row])
        if (len(result) <= 32767):
            sheet.write(row, clo_num - 1, result)
    for row in flag_reason_dict:
        flag_reason=flag_reason_dict[row]
        sheet.write(row,clo_num-2,flag_reason)
    if not  nlp_version_dict is {}:
        for row in nlp_version_dict:
            nlpVersion = nlp_version_dict[row]
            sheet.write(row, 3, nlpVersion)
    name = file[:len(file)-5] + str(datetime.now().strftime('%Y%m%d%H%M%S')) + "result.xls"
    result_paths = os.path.join(result_path, name)
    wb.save(result_paths)
    rate = float(allCase - failCase) / float(allCase)
    rate = '%.2f%%' % (rate * 100.0)
    fileName=file[:len(file)-5]
    if(len(fileName)<12):
        fileName+=" "*2*(12-len(fileName))
    allcase=str(allCase)
    if len(allcase)<6:
        allcase+=" "*(6-len(allcase))
    successCase=str(allCase - failCase)
    if len(successCase)<6:
        successCase+=" "*(6-len(successCase))
    failcase=str(failCase)
    if len(failcase)<6:
        failcase+=" "*(6-len(failcase))
    log = "#"+fileName+ " 总case数:" + allcase + "   成功case数:" + successCase + "   失败case数:" + failcase + "   成功率:" + str(rate)
    print (log)
    print ("大功告成！")
    return exit

def write_result_time(flag_dict,result_dict,flag_reason_dict,nlp_version,excel_path,file,result_path,exit):
    file_path = os.path.join(excel_path, file)
    rb = xlrd.open_workbook(filename=file_path)
    global sheetGlobal
    sheetGlobal= rb.sheet_by_index(0)
    clo_num = sheetGlobal.ncols
    wb = copy(rb)
    sheet = wb.get_sheet(0)
    red_style = xlwt.easyxf("font:colour_index red;")
    green_style = xlwt.easyxf("font:colour_index green;")
    allCase=len(flag_dict)
    failCase=0
    for row in flag_dict:
        flag = str(flag_dict[row])
        if flag == '成功':
            sheet.write(row, clo_num - 3, flag, green_style)
        if flag == '失败':
            exit = 1
            sheet.write(row, clo_num - 3, flag, red_style)
            failCase=failCase+1
    for row in result_dict:
        result = str(result_dict[row])
        if (len(result) <= 32767):
            sheet.write(row, clo_num - 1, result)
    for row in flag_reason_dict:
        flag_reason=flag_reason_dict[row]
        sheet.write(row,clo_num-2,flag_reason)
    for row in nlp_version:
        nlpVersion=nlp_version[row]
        sheet.write(row,3,nlpVersion)
    name = file[:len(file)-5] + str(datetime.now().strftime('%Y%m%d%H%M%S')) + "result.xls"
    result_paths = os.path.join(result_path, name)
    wb.save(result_paths)
    rate = float(allCase - failCase) / float(allCase)
    rate = '%.2f%%' % (rate * 100.0)
    fileName=file[:len(file)-5]
    if(len(fileName)<10):
        fileName+=" "*2*(10-len(fileName))
    allcase=str(allCase)
    if len(allcase)<6:
        allcase+=" "*(6-len(allcase))
    successCase=str(allCase - failCase)
    if len(successCase)<6:
        successCase+=" "*(6-len(successCase))
    failcase=str(failCase)
    if len(failcase)<6:
        failcase+=" "*(6-len(failcase))
    log = "#"+fileName+ " 总case数:" + allcase + "   成功case数:" + successCase + "   失败case数:" + failcase + "   成功率:" + str(rate)
    print (log)
    print ("大功告成！")
    return exit

def write_resultNew(flag_dict,category_dict,domain_dict,action_dict, result_dict, excel_path, file, result_path,exit):
    file_path = os.path.join(excel_path, file)
    rb = xlrd.open_workbook(filename=file_path)
    sheet = rb.sheet_by_index(0)
    clo_num = sheet.ncols
    wb = copy(rb)
    sheet = wb.get_sheet(0)
    red_style = xlwt.easyxf("font:colour_index red;")
    green_style = xlwt.easyxf("font:colour_index green;")
    for row in flag_dict:
        flag = str(flag_dict[row])
        if flag == '成功':
            sheet.write(row, clo_num - 5, flag, green_style)
        if flag == '失败':
            exit = 1
            sheet.write(row, clo_num - 5, flag, red_style)
        result = str(result_dict[row])
        if (len(result) <= 32767):
            sheet.write(row, clo_num - 1, result)
        category=str(category_dict[row])
        sheet.write(row,clo_num-4,category)
        domain=str(domain_dict[row])
        sheet.write(row,clo_num-3,domain)
        action=str(action_dict[row])
        sheet.write(row,clo_num-2,action)
    name = file[:len(file)-5] + str(datetime.now().strftime('%Y%m%d%H%M%S')) + "result.xls"
    result_paths = os.path.join(result_path, name)
    wb.save(result_paths)
    return exit

def write_error_result(result_path):
    book=xlwt.Workbook(encoding='utf-8')
    sheet=book.add_sheet('errorResult',cell_overwrite_ok=True)
    sheetData=book.add_sheet('dataStatistics',cell_overwrite_ok=True)
    sheetData.write(0,0,'fileName')
    sheetData.write(0,1,'allCaseNum')
    sheetData.write(0,2,'successCaseNum')
    sheetData.write(0,3,'failCaseNum')
    sheetData.write(0,4,'successRate')
    sheetData.col(0).width = 256 * 25
    sheetData.col(1).width = 256 * 16
    sheetData.col(2).width = 256 * 16
    sheetData.col(3).width = 256 * 16
    sheetData.col(4).width = 256 * 16
    ncols=sheetGlobal.ncols
    for clo in range(0,ncols):
        value=sheetGlobal.cell(0,clo).value
        sheet.write(0,clo,value)
    result_path=result_path.encode('utf8')
    files=os.listdir(result_path)
    fileNum=1
    num = 1
    for file in files:
        failNum = 1
        filePath=os.path.join(result_path,file)
        rbn=xlrd.open_workbook(filename=filePath)
        sheetFile=rbn.sheet_by_index(0)
        nrows=sheetFile.nrows
        for row in range(1,nrows):
            if str(sheetFile.cell(row,ncols - 3).value)=='失败':
                for clo in range(0,ncols):
                    value=sheetFile.cell(row,clo).value
                    sheet.write(num,clo,value)
                num=num+1
                failNum=failNum+1
        # file=file.decode('gb2312').encode('utf-8')
        sheetData.write(fileNum, 0, str(file[:len(file)-25],encoding='utf8'))
        sheetData.write(fileNum, 1, nrows - 1)
        sheetData.write(fileNum, 2, nrows - failNum)
        sheetData.write(fileNum, 3, failNum - 1)
        rate=float(nrows-failNum)/float(nrows-1)
        rate='%.2f%%' % (rate*100.0)
        sheetData.write(fileNum, 4, rate)
        log=str(file[:len(file)-25])+"   总case数:"+str((nrows-1))+"   成功case数:"+str((nrows - failNum))+"   失败case数:"+str((failNum-1))+"   成功率:"+str(rate)
        # print log
        fileNum=fileNum+1
    # error_name="所有入口失败语料整合"+str(datetime.now().strftime('%Y%m%d%H%M%S'))+".xls"
    error_name="ErrorResult"+str(datetime.now().strftime('%Y%m%d%H%M%S'))+".xls"
    error_result_path=os.path.join(result_path,bytes(error_name,encoding='utf8'))
    book.save(error_result_path)


def write_error_result1(result_path):
    book=xlwt.Workbook(encoding='utf-8')
    sheet=book.add_sheet('errorResult',cell_overwrite_ok=True)
    ncols=sheetGlobal.ncols
    for clo in range(0,ncols):
        value=sheetGlobal.cell(0,clo).value
        sheet.write(0,clo,value)
    result_path=result_path.encode('utf8')
    files=os.listdir(result_path)
    fileNum=1
    num = 1
    for file in files:
        failNum = 1
        filePath=os.path.join(result_path,file)
        rbn=xlrd.open_workbook(filename=filePath)
        sheetFile=rbn.sheet_by_index(0)
        nrows=sheetFile.nrows
        for row in range(1,nrows):
            if str(sheetFile.cell(row,ncols - 3).value)=='失败':
                for clo in range(0,ncols):
                    value=sheetFile.cell(row,clo).value
                    sheet.write(num,clo,value)
                num=num+1
                failNum=failNum+1
        # log=str(file[:len(file)-25])+"   总case数:"+str((nrows-1))+"   成功case数:"+str((nrows - failNum))+"   失败case数:"+str((failNum-1))+"   成功率:"+str(rate)
        # print log
        fileNum=fileNum+1
    # error_name="所有入口失败语料整合"+str(datetime.now().strftime('%Y%m%d%H%M%S'))+".xls"
    error_name="ErrorResult"+str(datetime.now().strftime('%Y%m%d%H%M%S'))+".xls"
    error_result_path=os.path.join(result_path,bytes(error_name,encoding='utf8'))
    book.save(error_result_path)

def findDevice(file):
    if ("app入口技能" in file):
        deviceId= "RRRR00000002"
    elif "热水器主控" in file:
        deviceId = "DDDD00000002"
    elif "app入口设备控制1" in file:
        # deviceId = "04FA83E45724"
        deviceId ="0007A8944FB5"
    elif "app入口设备控制2" in file:
        # deviceId= "DC330D4D1DEA"
        deviceId ="DC330D2EB337"
    elif ("x20入口设备控制" in file):
        deviceId= "000001"
    elif "1.0技能" in file:
        deviceId ="ABCDE10"
    elif "x20入口1" in file:
        deviceId = "ABCDE11"
    elif "x20入口2" in file:
        deviceId = "ABCDE12"
    elif "x20入口3" in file:
        deviceId = "ABCDE13"
    elif "x20入口4" in file:
        deviceId = "ABCDE14"
    else:
        deviceId="random123"
    return  deviceId

def isError(expect_retcode,retcode,responseFlag,category,expect_category,expect_domain,expect_action,action,actionList,domain):
    flag = "成功"
    flag_reason=""
    do_ac_list=[]
    try:
        expect_domain_list = expect_domain.split('|')
        domainIndex = expect_domain_list.index(domain) if (domain in expect_domain_list) else -1
        if '&' in expect_action:
            expect_action_list = expect_action.split('&')
            actionIndex = expect_action_list.index(action) if (action in expect_action_list) else -1
            if expect_domain==domain and expect_action_list==actionList :
                do_ac_flag = True
            else:
                do_ac_flag = False
        else:
            expect_action_list = expect_action.split('|')
            actionIndex = expect_action_list.index(action) if (action in expect_action_list) else -1
            for i in range(len(expect_domain_list)):
                do_ac = []
                do_ac.append(expect_domain_list[i])
                do_ac.append(expect_action_list[i])
                do_ac_list.append(do_ac)
            doac = []
            doac.append(domain)
            doac.append(action)
            if (doac in do_ac_list) or ((domain in expect_domain_list) and expect_action == "") or (
                    expect_domain == ""):
                do_ac_flag = True
            else:
                do_ac_flag = False
        if not ((str(expect_retcode) == str(retcode)) or (str(expect_retcode) == "")):
            flag = "失败"
            flag_reason += "返回码错误 "
        if not ((category == expect_category) or (expect_category == "")):
            flag = "失败"
            flag_reason += "category错误 "
        if not ((domainIndex >= 0) or (expect_domain == "")):
            flag = "失败"
            flag_reason += "domain错误 "
        if not ((actionIndex >= 0) or (expect_action == "")):
            flag = "失败"
            flag_reason += "action错误 "
        if not responseFlag:
            flag = "失败"
            flag_reason += "response或params错误 "
        if not do_ac_flag:
            flag = "失败"
            flag_reason += "意图解析错误 "
    except Exception as e:
        logging.exception(e)
        flag = "失败"
        flag_reason += "脚本错误 "
    return flag,flag_reason