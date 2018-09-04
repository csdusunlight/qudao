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
    url(r'^urls/$', views.UrlSet.as_view({'get': 'list'})),
    url(r'^url/(?P<pk>[0-9]+)/$', views.UrlSet.as_view({'get': 'retrieve'})),
    url(r'^tag/(?P<pk>[0-9]+)/$', views.TagSet.as_view({'get': 'retrieve'})),

    url(r'^articles/$', views.ArticleSet.as_view({'get': 'list'})),
    url(r'^get_most_hot_platform/$', 'newsm.views.get_project_investlog_company'),

    url(r'^article/(?P<pk>[0-9]+)/$', views.ArticleSet.as_view({
        'get':'retrieve',
    })),

    url(r'^article/(?P<pk>[0-9]+)/retrieve_by_published/$', views.ArticleSet.as_view({
                                                  'get':'retrieve_by_published',
                                                  })),
    url(r'^article/(?P<pk>[0-9]+)/lookup_by_tag/$', views.ArticleSet.as_view({
                                                 'get': 'lookup_by_tag'
    })),
    url(r'^articles/lookup_by_agroup/$', views.ArticleSet.as_view({
                                                 'get': 'lookup_by_agroup'
    })),
    url(r'^get_article_detail/$','newsm.views.get_article_detail',name='get_article_detail'),
    url(r'^get_article_list/$','newsm.views.get_article_list',name='get_article_list'),
    url(r'^agroups/$', views.AgroupSet.as_view({'get': 'list'})),
    url(r'^agroup/(?P<pk>[0-9]+)/$', views.AgroupSet.as_view({'get':'retrieve' }))
]
