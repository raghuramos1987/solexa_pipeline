import shutil
import os

class Copy(object):

    def __init__(self):
        pass

    def copy(self, src, dest):
        self.dest = dest
        self.fileList = src
        shutil.copy(src, dest)

    def copytree(self, src, path):
        self.dest = path 
        self.fileList = os.listdir(src)
        shutil.copytree(src, path)

if __name__=="__main__":
    a = Copy()
    os.system("touch temp.txt")
    a.copy("temp.txt", "temp")
