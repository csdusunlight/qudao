from django.conf.urls import url
from django.views.generic.base import TemplateView
from . import views

urlpatterns = [
#     url(r'^$', 'wafuli_admin.views.index', name='admin_index'),
    url(r'^preaudit_investlog/$', views.preaudit_investlog, name='preaudit_investlog'),
    url(r'^apply_projects/$', views.ApplyProjectList.as_view()),
    url(r'^apply_projects/(?P<pk>[0-9]+)/$', views.ApplyProjectDetail.as_view(), kwargs={'partial':True}),
    url(r'^margin_translog/$', views.TranslogList.as_view()),
    url(r'^margin_auditlog/$', views.MarginAuditLogList.as_view()),
]






