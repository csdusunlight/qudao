#coding:utf-8
'''
Created on 2018年5月31日

@author: lch
'''

import django.dispatch
register_signal = django.dispatch.Signal(providing_args=["user",])