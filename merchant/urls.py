from django.conf.urls import url
from django.views.generic.base import TemplateView
from . import views

urlpatterns = [
#     url(r'^$', 'wafuli_admin.views.index', name='admin_index'),
    url(r'^preaudit_investlog/$', views.preaudit_investlog, name='preaudit_investlog'),
    url(r'^stop_project/$', views.stop_project, name='stop_project'),
    url(r'^index/$', views.merchant, name='merchant_index'),     #jzy
    url(r'^merchant_detail_proj/$', views.merchant_detail_proj, name='merchant_detail_proj'),     #jzy
    url(r'^merchant_detail_day/$', views.merchant_detail_day, name='merchant_detail_day'),     #jzy
    url(r'^margin_manage/$', views.margin_manage, name='margin_manage'),
    url(r'^proj_manage/$', views.proj_manage, name='proj_manage'),      #jzy
    url(r'^proj_add/$', views.proj_add, name='proj_add'),     #llc
    url(r'^fangdan_audit/$', views.fangdan_audit, name='fangdan_audit'),        #jzy
    url(r'^apply_projects/$', views.ApplyProjectList.as_view()),
    url(r'^apply_projects/(?P<pk>[0-9]+)/$', views.ApplyProjectDetail.as_view(), kwargs={'partial':True}),
    url(r'^margin_translog/$', views.TranslogList.as_view()),
    url(r'^margin_auditlog/$', views.MarginAuditLogList.as_view()),
    url(r'^investlogs/$', views.InvestlogList.as_view()),
    url(r'^get_days_statis', views.get_days_statis, name='get_days_statis'),
    url(r'^get_project_statis_byday', views.get_project_statis_byday, name='get_project_statis_byday'),
    url(r'^projectstatislist/$', views.MerchantProjectStatisticsList.as_view()),
    url(r'^export_merchant_investlog/$', views.export_merchant_investlog, name='export_merchant_investlog'),
    url(r'^import_merchant_investlog/$', views.import_merchant_investlog, name='import_merchant_investlog'),
    url(r'^transfer/callback/$', views.transfer_callback, name='transfer_callback'),
    
]






