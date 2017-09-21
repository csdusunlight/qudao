from django.conf.urls import url
from django.views.generic.base import TemplateView


urlpatterns = [
    url(r'^$', 'wafuli_admin.views.index', name='admin_index'),
    url(r'^admin_apply/$', 'wafuli_admin.views.admin_apply', name='admin_apply'),
    url(r'^admin_office/$', 'wafuli_admin.views.admin_office', name='admin_office'),
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
    url(r'^import/$', 'wafuli_admin.views.import_invest_excel', name='import_invest_excel'),
    url(r'^export/$', 'wafuli_admin.views.export_invest_excel', name='export_invest_excel'),


    url(r'^export_withdraw/$', 'wafuli_admin.views.export_withdraw_excel', name='export_withdraw_excel'),
    url(r'^import_withdraw/$', 'wafuli_admin.views.import_withdraw_excel', name='import_withdraw_excel'),
    url(r'^export_charge/$', 'wafuli_admin.views.export_charge_excel', name='export_charge_excel'),

]






