#coding:utf-8
'''
Created on 20160222
'get':'lookup_by_tag'}
@author: lch
'''
from django.conf.urls import url,include
from django.views.generic.base import TemplateView
from newsm import views

urlpatterns = [
    url(r'^tags/$', views.TagSet.as_view({'get': 'list'})),
    url(r'^tag/(?P<pk>[0-9]+)/$', views.TagSet.as_view({'get': 'retrieve'})),

    url(r'^articles/$', views.ArticleSet.as_view({'get': 'list'})),

    url(r'^article/(?P<pk>[0-9]+)/$', views.ArticleSet.as_view({
                                                  'get':'retrieve',
                                                  })),
    url(r'^article/(?P<pk>[0-9]+)/lookup_by_tag/$', views.ArticleSet.as_view({
                                                 'get': 'lookup_by_tag'
    })),
    url(r'^agroups/$', views.AgroupSet.as_view({'get': 'list'})),
    url(r'^agroup/(?P<pk>[0-9]+)/$', views.AgroupSet.as_view({'get':'retrieve' }))
]
