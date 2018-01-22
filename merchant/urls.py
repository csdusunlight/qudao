from django.conf.urls import url
from django.views.generic.base import TemplateView
from . import views

urlpatterns = [
#     url(r'^$', 'wafuli_admin.views.index', name='admin_index'),
    url(r'^preaudit_investlog/$', views.preaudit_investlog, name='preaudit_investlog'),
    url(r'^merchant_index/$', views.merchant_index, name='merchant_index'),
    url(r'^bail_manage/$', views.bail_manage, name='bail_manage'),
    url(r'^proj_manage/$', views.proj_manage, name='proj_manage'),
    url(r'^fangdan_audit/$', views.fangdan_audit, name='fangdan_audit'),
    
]






