#coding:utf-8
'''
Created on 20160222

@author: lch
'''
from django.conf.urls import url,include
from django.views.generic.base import TemplateView
from wafuli import views
# url_about = [
#     url(r'^aboutus/$', 'wafuli.views.aboutus', name="about"),
#     url(r'^report/$', 'wafuli.views.report'),
#     url(r'^coop/$', 'wafuli.views.coop'),
#     url(r'^notice/$', 'wafuli.views.notice'),
#     url(r'^contact/$', 'wafuli.views.contact'),
#     url(r'^statement/$', 'wafuli.views.statement'),
# ]
urlpatterns = [
    url(r'^$', 'wafuli.views.index', name='index'),
    url(r'^project_all$', 'wafuli.views.project_all', name='project_all'),
    url(r'^user_guide/$', 'wafuli.views.user_guide', name='user_guide'),
    url(r'^screenshot/$', 'wafuli.views.display_screenshot', name='screenshot'),
    url(r'^qualification/$', 'wafuli.views.display_qualification', name='qualification'),
    url(r'^activity_rank/$', 'wafuli.views.activity_rank', name='activity_rank'),
    url(r'^cooperate/$',TemplateView.as_view(template_name='cooperation.html'), name='cooperate'), 
    url(r'^helpCenter/$',TemplateView.as_view(template_name='HelpCenter.html'), name='helpCenter'),
]
