#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
    Author:cleverdeng
    E-mail:clverdeng@gmail.com
"""
from django.conf import settings

__version__ = '0.9'
__all__ = ["PinYin"]

import os.path


class PinYin(object):
    def __init__(self):
        self.word_dict = {}
        self.dict_file = os.path.join(settings.STATIC_DIR, 'data/word.data').replace('\\','/')


    def load_word(self):
        if not os.path.exists(self.dict_file):
            raise IOError("NotFoundFile")

        with file(self.dict_file) as f_obj:
            for f_line in f_obj.readlines():
                try:
                    line = f_line.split('    ')
                    self.word_dict[line[0]] = line[1]
                except:
                    line = f_line.split('   ')
                    self.word_dict[line[0]] = line[1]


    def hanzi2pinyin(self, string="", firstcode=False):
        result = []
        result_fc = []
        if not isinstance(string, unicode):
            string = string.decode("utf-8")
        
        for char in string:
            key = '%X' % ord(char)
            value = self.word_dict.get(key, char)
            try:
                outpinyin = str(value).split()[0][:-1].lower()
            except:
                continue
            if not outpinyin:
                outpinyin = char
            result_fc.append(outpinyin[0])
            result.append(outpinyin)

        return result_fc, result


    def hanzi2pinyin_split(self, string="", split=""):
        result, result_fc = self.hanzi2pinyin(string=string)
        return split.join(result),split.join(result_fc)


if __name__ == "__main__":
    test = PinYin()
    test.load_word()
    string = "钓鱼岛是中国的"
    print "in: %s" % string
    print "out: %s" % str(test.hanzi2pinyin(string=string))
    print  test.hanzi2pinyin_split(string=string, split="-")
