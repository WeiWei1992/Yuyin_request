# -*- coding: utf-8 -*-
import os
dir_path="D:\yunPython\hundrods"
def read():
    # files = os.listdir(dir_path)
    # for file in files:
    #     file_path = os.path.join(dir_path, file)
    #     print file_path
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            filen=file.decode('gbk')
            filenn=filen[:len(filen)-4]
            print filenn
if __name__ == '__main__':
    read()
