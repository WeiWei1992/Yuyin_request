from Nlp_interface.main import autoNlp
import os
import logging
import logging.config
CON_LOG='log.conf'
logging.config.fileConfig(CON_LOG)
logging=logging.getLogger()

if __name__=="__main__":
    logging.info("开始测试.........................................")
    #os.system("pause")
    case_filepath = "D:\\Python_Project\\yuyin_request\\Nlp_interface\\case\\case.xlsx"
    autoNlp(case_filepath)
    logging.info("测试结束.....................................")
    os.system("pause")
