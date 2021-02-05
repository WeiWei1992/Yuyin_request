import os
from Nlp_interface.send_url import send_url,handle_response
from Nlp_interface.operate_excel import handle_casedata,creat_excel,save_excel
from Nlp_interface.judge import judeg_res
from tkinter import scrolledtext
from tkinter import *
import re
import logging
import logging.config
CON_LOG='log.conf'
logging.config.fileConfig(CON_LOG)
logging=logging.getLogger()
import time
def autoNlp(text,casePath,sheet=None):
    cases=handle_casedata(casePath)
    result_path=creat_excel()
    logging.info("====")
    logging.info(cases)
    for case in cases:
        logging.info("测试用例 ----"+str(case['id'])+" ----" +str(case['name']))
        #tmp="测试用例 ----"+str(case['id'])+" ----" +str(case['name']+"\n")
        # text.insert(END,tmp)
        logging.info(case)
        if case['isrun']=='N' or case['isrun']=='n' or case['isrun']=="No" or case['isrun']=='no':
            logging.warning("略过该用例")
            flag=''
            fail_resons=''
            all_response=''
            sign=0
            save_excel(result_path, case, flag=flag, fail_reasons=fail_resons, response=all_response,sign=sign,sheet=None)
            continue
        else:

            query=case['query']
            response = send_url(query=query)
            all_response, res=handle_response(response)
            logging.info("handle_response 返回的结果  ")
            logging.info("all_response:   "+str(all_response))
            logging.info("res:   "+str(res))

            flag, fail_resons, res ,sign= judeg_res(case, res)
            logging.info("juede_res 返回的结果")
            logging.info("flag:  "+str(flag))
            logging.info("fail_reasons: "+str(fail_resons))
            logging.info("res: "+str(res))

            tmp = "测试用例--" + str(case['id']) + "--" + str(case['name'] +"--结果--"+str(flag)+"\n")
            text.insert(END,tmp)
            text.see(END)

            save_excel(result_path,case,flag=flag,fail_reasons=fail_resons,response=all_response,sign=sign,sheet=None)
            time.sleep(1)



if __name__=="__main__":
    case_filepath = "D:\\Python_Project\\yuyin_request\\Nlp_interface\\case\\case.xlsx"
    autoNlp(case_filepath)