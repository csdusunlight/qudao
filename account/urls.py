from django.conf.urls import url
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^$', 'account.views.account', name='account_index'),
    url(r'^hongbao/$', 'account.views.hongbao', name='account_hongbao'),    #jzy
    url(r'^money/$', 'account.views.money', name='account_money'),
    url(r'^yuyue/$', 'account.views.yuyue', name='account_yuyue'),
#     url(r'^moneypage/$', 'account.views.get_user_money_page', name='get_user_money_page'),
    url(r'security/$', 'account.views.security', name='account_security'),
#     url(r'^bankcard/$', 'account.views.bankcard', name='account_bankcard'),
    url(r'^withdraw/$', 'account.views.withdraw', name='account_withdraw'),
    url(r'^message/$', 'account.views.message', name='account_message'),
#     url(r'^messagepage/$', 'account.views.get_user_message_page', name='get_user_message_page'),
    url(r'^register/$', 'account.views.register', name='register'),
    url(r'^register_from_gzh/$', 'account.views.register_from_gzh', name='register_from_gzh'),
    url(r'^login/$', 'account.views.login', {'template_name': 'registration/login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'template_name': 'registration/logged_out.html', 'next_page':'login'}, name='logout'),
#     url(r'signin/$', 'account.views.signin', name='signin'),
    url(r'^password_change/$', 'account.views.password_change', name='password_change'),
    url(r'^change_pay_password/$', 'account.views.change_pay_password', name='change_pay_password'),
    url(r'^bind_bankcard/$', 'account.views.bind_bankcard', name='bind_bankcard'),
    url(r'^bind_zhifubao/$', 'account.views.bind_zhifubao', name='bind_zhifubao'),
    url(r'^bind_bankcard_page/$', 'account.views.m_bind_bankcard_page', name='bind_bankcard_page'),
    url(r'^change_bankcard_page/$', 'account.views.m_change_bankcard_page', name='change_bankcard_page'),
    url(r'^bind_zhifubao_page/$', 'account.views.m_bind_zhifubao_page', name='bind_zhifubao_page'),
    url(r'^change_zhifubao_page/$', 'account.views.m_change_zhifubao_page', name='change_zhifubao_page'),
#     url(r'^password_change/done/$', auth_views.password_change_done, name='password_change_done'),
#     url(r'^password_reset/$', auth_views.password_reset, name='password_reset'),
#     url(r'^password_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
#     url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
#         auth_views.password_reset_confirm, name='password_reset_confirm'),
#     url(r'^reset/done/$', auth_views.password_reset_complete, name='password_reset_complete'),
    url(r'^verifymobile/$', 'account.views.verifymobile', name='verifymobile'),
    url(r'^verifyusername/$', 'account.views.verifyusername', name='verifyusername'),
    url(r'^verifyqq/$', 'account.views.verifyqq', name='verifyqq'),
    url(r'^verify_domain/$', 'account.views.verify_domainName', name='verify_domain'),
    url(r'^verifyinviter/$', 'account.views.verifyinviter', name='verifyinviter'),
    url(r'^phoneImageV/$', 'account.views.phoneImageV', name='phoneImageV'),
#    url(r'verifytelcode/$', 'account.views.verifytelcode', name='verifytelcode'),
#     url(r'^callback/$', 'account.views.callbackby189', name='callback'),
#
    url(r'^resetpw/$', 'account.forgot_passwd.forgot_passwd', name='forgot_passwd'),
    url(r'^forgot_validate_randcode/$', 'account.forgot_passwd.validate_randcode', name='forgot-validate-randcode'),
    url(r'^forgot_validate_telcode/$', 'account.forgot_passwd.validate_telcode', name='forgot-validate-telcode'),
#
    url(r'^channel/$', 'account.channel.channel', name='account_channel'),
    url(r'^export_investlog/$', 'account.channel.export_investlog', name='export_investlog'),
    url(r'^import_investlog/$', 'account.channel.import_investlog', name='import_investlog'),
#
    url(r'^submit_itembyitem/$', 'account.channel.submit_itembyitem', name='submit_itembyitem'),
    url(r'^submit_excel_all/$', 'account.channel.import_investlog_all', name='submit_excel_all'),
#     url(r'^revise_project/$', 'account.channel.revise_project', name='revise_project'),
#
# url(r'^get_nums$', 'account.views.get_nums', name='get_nums'),
    url(r'^account_setting/$', 'account.views.account_setting', name='account_setting'),
    url(r'^account_notice/$', 'account.views.account_notice', name='account_notice'),
    url(r'^account_submit/$', 'account.channel.channel', name='account_submit'),
    url(r'^account_audited/$', 'account.views.account_audited', name='account_audited'),
    url(r'^account_audited_2/$', 'account.views.account_audited_2', name='account_audited_2'),

    url(r'^project/$', 'account.views.project_manage', name='project_manage'),
#     url(r'^project_create/$', 'account.views.project_create', name='project_create'),
    url(r'^submit_screenshot/$', 'account.views.submit_screenshot', name='submit_screenshot'),

    url(r'^admin_invest/(?P<id>[0-9]+)/$', 'account.views.admin_investlog', name='admin_investlog'),
#     url(r'^personal-project/(?:(?P<id>[0-9]+)/)?$', 'account.views.project_add', name='personal-project'),
    url(r'^create_update_selfproject/(?:(?P<id>[0-9]+)/)?$', 'account.project.create_update_selfproject', name='create_update_selfproject'),
    url(r'^update_offiproject/(?P<id>[0-9]+)/$', 'account.project.update_offiproject', name='update_offiproject'),
    url(r'^delete_selfproject/(?P<id>[0-9]+)/$', 'account.project.delete_selfproject', name='delete_selfproject'),
    
    url(r'^detail_investlog/(?P<id>[0-9]+)/$', 'account.views.detail_investlog', name='detail_investlog'),
    
    url(r'^quick-submit/$', 'account.views.quick_sumbit', name='quick_submit'),
    url(r'^detail/project/(?P<id>[0-9]+)/$', 'account.views.detail_project', name='detail_project'),
    url(r'^submitOrder/$', 'account.views.submitOrder', name='submitOrder'),
    
    url(r'^reaudit/$', 'account.views.reaudit', name='reaudit'),
    url(r'^apply_for_channel_user/$', 'account.views.apply_for_channel_user', name='apply_for_channel'),
    url(r'^apply_for_fangdan_user/$', 'account.views.apply_for_fangdan_user', name='apply_for_fangdan'),

    #    url(r'^sitemessage/(?P<id>[0-9]+)/$', 'account.views.sitemessage.as_views()', name='sitemessage'),

]
