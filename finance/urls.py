#coding:utf-8
'''
Created on 20170605

@author: lch
'''
from django.conf.urls import url,include
from django.views.generic.base import TemplateView
from . import views
# url_about = [
#     url(r'^aboutus/$', 'wafuli.views.aboutus', name="about"),
#     url(r'^report/$', 'wafuli.views.report'),
#     url(r'^coop/$', 'wafuli.views.coop'),
#     url(r'^notice/$', 'wafuli.views.notice'),
#     url(r'^contact/$', 'wafuli.views.contact'),
#     url(r'^statement/$', 'wafuli.views.statement'),
# ]
urlpatterns = [
    url(r'^$', views.finance_page),#post参数：ids
    url(r'^check_transfer$', views.submit_transfer),#post参数：ids
    url(r'^submit_transfer', views.submit_transfer),#post参数：ids
    url(r'^export_investlog$', views.export_investlog_for_pay),
    url(r'^import_investlog', views.import_investlog_for_pay),
    url(r'^mark_pay_state', views.mark_pay_state),#post参数：ids， state（state：1, 打款失败标记为未打款， state：3， 未打款标记为已打款）
]
