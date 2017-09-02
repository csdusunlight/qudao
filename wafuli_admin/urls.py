from django.conf.urls import url
from django.views.generic.base import TemplateView


urlpatterns = [
    url(r'^$', 'wafuli_admin.views.index', name='admin_index'),
    url(r'^indexpage/$', 'wafuli_admin.views.get_admin_index_page', name='get_admin_index_page'),
    url(r'^admin_task/$', 'wafuli_admin.views.admin_task', name='admin_task'),
    url(r'^admin_media/$', 'wafuli_admin.views.admin_media', name='admin_media'),       #jzy
    url(r'^admin_finance/$', 'wafuli_admin.views.admin_finance', name='admin_finance'),
    url(r'^finance_page/$', 'wafuli_admin.views.get_admin_finance_page', name='get_admin_finance_page'),
    url(r'^task_page/$', 'wafuli_admin.views.get_admin_task_page', name='get_admin_task_page'),
    url(r'^admin_user/$', 'wafuli_admin.views.admin_user', name='admin_user'),
    url(r'^admin_channel/$', TemplateView.as_view(template_name="admin_channel.html"), name='admin_channel'),
    url(r'^userpage/$', 'wafuli_admin.views.get_admin_user_page', name='get_admin_user_page'),
    url(r'^channelpage/$', 'wafuli_admin.channel.get_admin_channel_page', name='get_admin_channel_page'),
    url(r'^admin_withdraw/$', 'wafuli_admin.views.admin_withdraw', name='admin_withdraw'),
    url(r'^withpage/$', 'wafuli_admin.views.get_admin_with_page', name='get_admin_with_page'),
    url(r'^admin_score$', 'wafuli_admin.views.admin_score', name='admin_score'),
    url(r'^scorepage/$', 'wafuli_admin.views.get_admin_score_page', name='get_admin_score_page'),
    url(r'^admin_recommend_return/$', 'wafuli_admin.activity.admin_recommend_return', name='admin_recommend_return'),
    url(r'^return_recommend_page/$', 'wafuli_admin.activity.get_admin_recommend_return_page', name='get_admin_recommend_return_page'),

    url(r'^deliver_coupon/$', 'wafuli_admin.coupon.deliver_coupon', name='deliver_coupon'),
    url(r'^get_project_list/$', 'wafuli_admin.coupon.get_project_list', name='get_project_list'),
    url(r'^parse_file/$', 'wafuli_admin.coupon.parse_file', name='parse_file'),
    url(r'^admin_coupon/$', 'wafuli_admin.coupon.admin_coupon', name='admin_coupon'),
    url(r'^admin_coupon_page/$', 'wafuli_admin.coupon.get_admin_coupon_page', name='get_admin_coupon_page'),

    url(r'^admin_charge/$', 'wafuli_admin.views.admin_charge', name='admin_charge'),
    url(r'^chargepage/$', 'wafuli_admin.views.get_admin_charge_page', name='get_admin_charge_page'),

    url(r'^admin_investrecord/$', 'wafuli_admin.views.admin_investrecord', name='admin_investrecord'),
    url(r'^investrecordpage/$', 'wafuli_admin.views.get_admin_investrecord_page', name='get_admin_investrecord_page'),
    url(r'^send_multiple_msg/$', 'wafuli_admin.views.send_multiple_msg', name='send_multiple_msg'),

#     url(r'^parse_excel/$', 'wafuli_admin.channel.parse_excel', name='parse_excel'),
    url(r'^import/$', 'wafuli_admin.views.import_finance_excel', name='import_finance_excel'),
    url(r'^export/$', 'wafuli_admin.views.export_finance_excel', name='export_finance_excel'),

    url(r'^export_conpon/$', 'wafuli_admin.coupon.export_coupon_excel', name='export_coupon_excel'),
    url(r'^import_conpon/$', 'wafuli_admin.coupon.import_coupon_excel', name='import_coupon_excel'),

    url(r'^export_withdraw/$', 'wafuli_admin.views.export_withdraw_excel', name='export_withdraw_excel'),
    url(r'^import_withdraw/$', 'wafuli_admin.views.import_withdraw_excel', name='import_withdraw_excel'),
    url(r'^export_charge/$', 'wafuli_admin.views.export_charge_excel', name='export_charge_excel'),
    
    url(r'^export_media/$', 'wafuli_admin.views.export_media_excel', name='export_media_excel'),
    url(r'^import_media_excel/$', 'wafuli_admin.views.import_media_excel', name='import_media_excel'),
]






