import os
import sys
import shutil
def fildAllFiles(path):
    files=[]
    for root,ds,fs in os.walk(path):
        # print(root)
        # print(ds)
        # print(fs)
        files=fs

    return files

if __name__=="__main__":
    path='D:\\Yinqing\\1224\\PCM_1412\\PCM_1412'
    files=fildAllFiles(path)
    print(files)