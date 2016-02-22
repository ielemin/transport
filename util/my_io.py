__author__ = 'adrien'

import os
import codecs
import re
import datetime
import glob

defaultencoding = 'utf-8-sig'
#abspath = '../../../../../dev/python/GoogleAPI'
abspath = '..'

class myIO:
    abspath = '..'

    @staticmethod
    def GetTimeAsString():
        now = datetime.datetime.now()
        return '{:%Y%m%d_%H%M%S}'.format(now)

    @staticmethod
    def GetUniqueName(filePath, fileName, ext=''):
        fileName += "_" + myIO.GetTimeAsString()
        if not (os.path.exists(filePath)):
            os.makedirs(filePath)
        while os.path.exists(filePath + '/' + fileName + ext):
            fileName += '@'
        return filePath + '/' + fileName + ext

    @staticmethod
    def GetMostRecentFromTemplate(filePath, fileNameTemplate):
        if not (os.path.exists(filePath)):
            return
        newestTimestamp = 0
        newestFile = ""
        for file in glob.glob('%s/*%s*' % (filePath, fileNameTemplate)):
            lastModTime = os.stat(file).st_mtime
            if (lastModTime > newestTimestamp):
                newestTimestamp = lastModTime
                newestFile = file
        return newestFile

    @staticmethod
    def GetFileWrite(fileFullName, encoding=defaultencoding):
        return codecs.open(fileFullName, 'w', encoding=encoding)

    @staticmethod
    def GetFileRead(fileFullName, encoding=defaultencoding):
        if not (fileFullName):
            return
        if not (os.path.exists(fileFullName)):
            return

        return codecs.open(fileFullName, 'r', encoding=encoding)

    @staticmethod
    def u_to_floatArray(unicode):
        uArray = re.findall(r"[-+]?\d*\.\d+|[-+]?\d+", unicode)
        fArray = []
        for uItem in uArray:
            fArray.append(float(uItem))
        return fArray

    @staticmethod
    def u_to_intArray(unicode):
        uArray = re.findall(r"[-+]?\d+", unicode)
        dArray = []
        for uItem in uArray:
            dArray.append(int(uItem))
        return dArray