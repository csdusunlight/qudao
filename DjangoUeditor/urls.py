#coding:utf-8

from django.conf.urls import patterns, url


from views import get_ueditor_controller
from django.views.generic.base import TemplateView

urlpatterns = patterns('',
    url(r'^controller/$',get_ueditor_controller),
    url(r'^$', TemplateView.as_view(template_name="test.html"))
)