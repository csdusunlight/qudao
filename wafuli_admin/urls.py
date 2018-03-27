from django.conf.urls import url
from django.views.generic.base import TemplateView
from wafuli_admin import merchant_admin, coupon_admin


urlpatterns = [
    url(r'^$', 'wafuli_admin.views.index', name='admin_index'),
    url(r'^admin_merchant_look/$', 'wafuli_admin.views.admin_merchant_look', name='admin_merchant_look'),
    url(r'^admin_apply/$', 'wafuli_admin.views.admin_apply', name='admin_apply'),
    url(r'^admin_office/$', 'wafuli_admin.views.admin_invest', name='admin_office'),
    url(r'^admin_private/$', 'wafuli_admin.views.admin_private', name='admin_private'),
#     url(r'^indexpage/$', 'wafuli_admin.views.get_admin_index_page', name='get_admin_index_page'),
    url(r'^admin_invest/$', 'wafuli_admin.views.admin_invest', name='admin_invest'),
#     url(r'^invest_page/$', 'wafuli_admin.views.get_admin_invest_page', name='get_admin_invest_page'),
    url(r'^admin_user/$', 'wafuli_admin.views.admin_user', name='admin_user'),
#     url(r'^userpage/$', 'wafuli_admin.views.get_admin_user_page', name='get_admin_user_page'),
    url(r'^admin_withdraw/$', 'wafuli_admin.views.admin_withdraw', name='admin_withdraw'),
    url(r'^withpage/$', 'wafuli_admin.views.get_admin_with_page', name='get_admin_with_page'),


    url(r'^admin_charge/$', 'wafuli_admin.views.admin_charge', name='admin_charge'),
    url(r'^chargepage/$', 'wafuli_admin.views.get_admin_charge_page', name='get_admin_charge_page'),

    url(r'^send_multiple_msg/$', 'wafuli_admin.views.send_multiple_msg', name='send_multiple_msg'),

#     url(r'^parse_excel/$', 'wafuli_admin.channel.parse_excel', name='parse_excel'),
    url(r'^import_investlog/$', 'wafuli_admin.views.import_investlog', name='admin_import_investlog'),
    url(r'^export_investlog/$', 'wafuli_admin.views.export_investlog', name='admin_export_investlog'),


    url(r'^export_withdraw/$', 'wafuli_admin.views.export_withdrawlog', name='export_withdraw_excel'),
    url(r'^import_withdraw/$', 'wafuli_admin.views.import_withdrawlog', name='import_withdraw_excel'),
    url(r'^export_charge/$', 'wafuli_admin.views.export_charge_excel', name='export_charge_excel'),
    
    url(r'^award_logs/$', 'wafuli_admin.views.award_logs', name='award_logs'),
    
    url(r'^batch_withdraw/$', 'wafuli_admin.views.batch_withdraw', name='batch_withdraw'),
    
    url(r'^admin_merchant_project/$', merchant_admin.admin_merchant_project, name='admin_merchant_project'),
    url(r'^admin_merchant_investlog/$', merchant_admin.admin_merchant_investlog, name='admin_merchant_investlog'),
    url(r'^admin_margin_query/$', merchant_admin.admin_margin_query, name='admin_margin_query'),
    url(r'^admin_margin/$', merchant_admin.admin_margin, name='admin_margin'),
#     url(r'^admin_merchant/$', 'wafuli_admin.views.admin_apply', name='admin_apply'),
#     url(r'^preaudit/$', 'wafuli_admin.views.admin_invest', name='admin_office'),
    url(r'^admin_export_merchant_investlog/$', merchant_admin.admin_export_merchant_investlog, name='admin_export_merchant_investlog'),
    url(r'^admin_import_merchant_investlog/$', merchant_admin.admin_import_merchant_investlog, name='admin_import_merchant_investlog'),

    url(r'^check_new/$', merchant_admin.check_new, name='check_new'),
    
    url(r'^deliver_coupon/$', coupon_admin.deliver_coupon, name='deliver_coupon'),
    url(r'^parse_file/$', coupon_admin.parse_file, name='parse_file'),
]






