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
    text.insert(END,"��ʼ����.....\n")
    autoNlp(text,case_path)
    text.insert(END,"���Խ���....\n")


def _ui():
    root=Tk()
    root.title("����NLP�ӿ��Զ�������")

    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()

    ww = 100
    wh = 100
    # x=(sw-ww)/2
    # y=((sh-wh)/5)*3
    x = 600
    y = 400

    root.geometry("%dx%d+%d+%d" % (x, y, ww, wh))

    title = Label(root, text="    ����NLP�ӿ��Զ�������", compound=CENTER, font=("΢���ź�", 20))
    title.grid(row=0, columnspan=3, sticky=E + W)

    case_path=StringVar()
    case_path_label=Label(root,text="����·��",foreground="white",background="blue")
    case_path_label.grid(sticky=E, padx=10, pady=10)
    case_path_entry = Entry(root, textvariable=case_path, width=60)
    case_path_entry.grid(row=1, column=1, sticky=W)

    def selecctPath():
        path_ = filedialog.askopenfilename(initialdir=casedir)
        print(path_)
        case_path.set(path_)

    Button(root, text="·��ѡ��", command=selecctPath).grid(row=1, column=2)

    #text = scrolledtext.ScrolledText(root, width=60, height=10)
    text = scrolledtext.ScrolledText(root, width=60, height=20)

    text.grid(row=2, column=1, columnspan=1, sticky=W)

    def click():
        logging.info("����˿�ʼ���԰�ť����ʼ����")
        case_path=case_path_entry.get()
        logging.info("��ȡ��������·���ǣ� "+str(case_path))

        # ���һ���߳�ȥ����
        th = threading.Thread(target=handle, args=(text,case_path))

        th.setDaemon(True)  # �����ػ��̣߳����߳̽����󣬸��߳�ҲҪ����
        th.start()
        pass

    click_btn = Button(root, text="��ʼ����", command=click)
    click_btn.grid(row=3, column=0)

    root.mainloop()

if __name__=="__main__":
    _ui()