from django.conf.urls import url
from django.views.generic.base import TemplateView
from . import views

urlpatterns = [
#     url(r'^$', 'wafuli_admin.views.index', name='admin_index'),
    url(r'^preaudit_investlog/$', views.preaudit_investlog, name='preaudit_investlog'),
    url(r'^stop_project/$', views.stop_project, name='stop_project'),
    url(r'^merchant_index/$', views.merchant_index, name='merchant_index'),     #jzy
    url(r'^bail_manage/$', views.bail_manage, name='bail_manage'),      #jzy
    url(r'^proj_manage/$', views.proj_manage, name='proj_manage'),      #jzy
    url(r'^proj_add/$', views.proj_add, name='proj_add'),     #llc
    url(r'^fangdan_audit/$', views.fangdan_audit, name='fangdan_audit'),        #jzy
    url(r'^apply_projects/$', views.ApplyProjectList.as_view()),
    url(r'^apply_projects/(?P<pk>[0-9]+)/$', views.ApplyProjectDetail.as_view(), kwargs={'partial':True}),
    url(r'^margin_translog/$', views.TranslogList.as_view()),
    url(r'^margin_auditlog/$', views.MarginAuditLogList.as_view()),

]






