# -*- coding: gbk -*-
import tkinter
from tkinter import *
from tkinter import filedialog
# import tkinter.messagebox
# from tkinter.filedialog import askdirectory
import threading
from tkinter import scrolledtext

from Nlp_interface.main import autoNlp
import os
import logging
import logging.config
CON_LOG='log.conf'
logging.config.fileConfig(CON_LOG)
logging=logging.getLogger()

casedir1=os.getcwd()
casedir=os.path.join(casedir1,'case')
# print(casedir)

from Nlp_interface.main import autoNlp

def handle(text,case_path):
    text.insert(END,"开始测试.....\n")
    autoNlp(text,case_path)
    text.insert(END,"测试结束....\n")


def _ui():
    root=Tk()
    root.title("音箱NLP接口自动化测试")

    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()

    ww = 100
    wh = 100
    # x=(sw-ww)/2
    # y=((sh-wh)/5)*3
    x = 600
    y = 400

    root.geometry("%dx%d+%d+%d" % (x, y, ww, wh))

    title = Label(root, text="    音箱NLP接口自动化测试", compound=CENTER, font=("微软雅黑", 20))
    title.grid(row=0, columnspan=3, sticky=E + W)

    case_path=StringVar()
    case_path_label=Label(root,text="用例路径",foreground="white",background="blue")
    case_path_label.grid(sticky=E, padx=10, pady=10)
    case_path_entry = Entry(root, textvariable=case_path, width=60)
    case_path_entry.grid(row=1, column=1, sticky=W)

    def selecctPath():
        path_ = filedialog.askopenfilename(initialdir=casedir)
        print(path_)
        case_path.set(path_)

    Button(root, text="路径选择", command=selecctPath).grid(row=1, column=2)

    #text = scrolledtext.ScrolledText(root, width=60, height=10)
    text = scrolledtext.ScrolledText(root, width=60, height=20)

    text.grid(row=2, column=1, columnspan=1, sticky=W)

    def click():
        logging.info("点击了开始测试按钮，开始测试")
        case_path=case_path_entry.get()
        logging.info("获取到的用例路径是： "+str(case_path))

        # 添加一个线程去处理
        th = threading.Thread(target=handle, args=(text,case_path))

        th.setDaemon(True)  # 设置守护线程，主线程结束后，该线程也要结束
        th.start()
        pass

    click_btn = Button(root, text="开始测试", command=click)
    click_btn.grid(row=3, column=0)

    root.mainloop()

if __name__=="__main__":
    _ui()