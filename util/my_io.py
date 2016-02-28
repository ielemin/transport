import os
import codecs
import re
import datetime
import glob

__author__ = 'ielemin'

default_encoding = 'utf-8-sig'
# abspath = '../../../../../dev/python/GoogleAPI'
abspath = '..'


class MyIO:
    abspath = '..'

    @staticmethod
    def get_time_as_string():
        now = datetime.datetime.now()
        return '{:%Y%m%d_%H%M%S}'.format(now)

    @staticmethod
    def get_unique_name(file_path, file_name, ext=''):
        file_name += "_" + MyIO.get_time_as_string()
        if not (os.path.exists(file_path)):
            os.makedirs(file_path)
        while os.path.exists(file_path + '/' + file_name + ext):
            file_name += '@'
        return file_path + '/' + file_name + ext

    @staticmethod
    def get_most_recent_from_template(file_path, file_name_template):
        if not (os.path.exists(file_path)):
            return
        newest_timestamp = 0
        newest_file = ""
        for file in glob.glob('%s/*%s*' % (file_path, file_name_template)):
            last_mod_time = os.stat(file).st_mtime
            if last_mod_time > newest_timestamp:
                newest_timestamp = last_mod_time
                newest_file = file
        return newest_file

    @staticmethod
    def get_file_write(file_full_name, encoding=default_encoding):
        return codecs.open(file_full_name, 'w', encoding=encoding)

    @staticmethod
    def get_file_read(file_full_name, encoding=default_encoding):
        if not file_full_name:
            return
        if not (os.path.exists(file_full_name)):
            return

        return codecs.open(file_full_name, 'r', encoding=encoding)

    @staticmethod
    def u_to_float_array(unicode):
        u_array = re.findall(r"[-+]?\d*\.\d+|[-+]?\d+", unicode)
        f_array = []
        for uItem in u_array:
            f_array.append(float(uItem))
        return f_array

    @staticmethod
    def u_to_int_array(unicode):
        u_array = re.findall(r"[-+]?\d+", unicode)
        d_array = []
        for uItem in u_array:
            d_array.append(int(uItem))
        return d_array
