#coding:utf-8
'''
Created on 20170703

@author: lch
'''

from django.conf.urls import url
from project_admin import views
from rest_framework.urlpatterns import format_suffix_patterns
urlpatterns = [
    url(r'^contacts/$', views.ContactList.as_view()),
    url(r'^contacts/(?P<pk>[0-9]+)/$', views.ContactDetail.as_view(), kwargs={'partial':True}),
    url(r'^platform/$', views.PlatformList.as_view()),
    url(r'^platform/(?P<pk>[0-9]+)/$', views.PlatformDetail.as_view(), kwargs={'partial':True}),
    url(r'^projects/$', views.ProjectList.as_view()),
    url(r'^projects/(?P<pk>[0-9]+)/$', views.ProjectDetail.as_view(), kwargs={'partial':True}),
    url(r'^investdata/$', views.ProjectInvestDataList.as_view()),
    url(r'^investdata/(?P<pk>[0-9]+)/$', views.ProjectInvestDataDetail.as_view()),
    url(r'^projectstatis/$', views.ProjectStatisList.as_view()),
    url(r'^daystatis/$', views.DayStatisList.as_view()),
    url(r'^account/$', views.AccountList.as_view()),
    url(r'^account/(?P<pk>[0-9]+)/$', views.AccountDetail.as_view()),
    url(r'^accountbill/$', views.AccountBillList.as_view()),
    url(r'^accountbill/(?P<pk>[0-9]+)/$', views.AccountBillDetail.as_view()),
    url(r'^dayaccountstatis/$', views.DayAccountStatisList.as_view()),
]
from django.conf.urls import include


urlpatterns = format_suffix_patterns(urlpatterns)
urlpatterns += [
    url(r'^api-auth/', include('rest_framework.urls',namespace='rest_framework')),
    url(r'^$', views.project_index, name='project_index'),
    url(r'^project_data/$', views.project_data, name='project_data'),
    url(r'^project_finance/$', views.project_finance, name='project_finance'),
    url(r'^project_settle/$', views.project_settle, name='project_settle'),

    # 综合管理部分修改
    url(r'^project_detail/$', views.project_detail, name='project_detail'),
    url(r'^project_status/$', views.project_status, name='project_status'),
    url(r'^jiafang_detail/$', views.jiafang_detail, name='jiafang_detail'),
    url(r'^finance_pandect/$', views.finance_pandect, name='finance_pandect'),
    url(r'^account_manage/$', views.account_manage, name='account_manage'),
    url(r'^account_detail/$', views.account_detail, name='account_detail'),
    url(r'^contacts_detail/$', views.contacts_detail, name='contacts'),
    url(r'^contacts_detail/(?P<id>[0-9]*)/$', views.contacts_detail, name='contacts_detail'),   #jzy

    url(r'^import_projectdata_excel/$', views.import_projectdata_excel, name='import_projectdata_excel'),
    url(r'^import_audit_projectdata_excel/$', views.import_audit_projectdata_excel, name='import_audit_projectdata_excel'),
    url(r'^export_investdata_excel/$', views.export_investdata_excel, name='export_investdata_excel'),
    url(r'^export_account_bill_excel/$', views.export_account_bill_excel, name='export_account_bill_excel'),
]
