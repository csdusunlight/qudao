'''
Created on 20160222

@author: lch
'''
from django.conf.urls import url,include
from django.views.generic.base import TemplateView
from wafuli import views, mediaproject, rest
# url_about = [
#     url(r'^aboutus/$', 'wafuli.views.aboutus', name="about"),
#     url(r'^report/$', 'wafuli.views.report'),
#     url(r'^coop/$', 'wafuli.views.coop'),
#     url(r'^notice/$', 'wafuli.views.notice'),
#     url(r'^contact/$', 'wafuli.views.contact'),
#     url(r'^statement/$', 'wafuli.views.statement'),
# ]
urlpatterns = [
    url(r'^$', 'wafuli.views.wfl_index', name='index'),     #jzy
#    url(r'^(?P<board>\S+)/$', 'wafuli.views.board', name='board'),
    # url(r'^finance/$', 'wafuli.views.finance', name='finance'),
    # url(r'^finance/(?P<id>[0-9]*)/$', 'wafuli.views.finance', name='finance_detail'),
    url(r'^finance/$', 'wafuli.finance.finance', name='finance'),     #jzy
    url(r'^finance/(?P<id>[0-9]*)/$', 'wafuli.finance.finance', name='finance_detail'),   #jzy
    url(r'^add_finance/$', 'wafuli.finance.add_finance', name='add_finance'),     #jzy
    url(r'^task/$', 'wafuli.views.task', name='task'),
    url(r'^task/(?P<id>[0-9]*)/$', 'wafuli.views.task', name='task_detail'),
#     url(r'^welfare/(?:(?P<id>[0-9]*)/)?$', 'wafuli.welfare.welfare', name='welfare'),
#     url(r'^welfare/(?:(?P<type>hb|yhq|by)/)?(?:list-page(?P<page>[0-9]*)/)?$', 'wafuli.welfare.welfare', name='welfare_list'),
    url(r'^mall/$', 'wafuli.views.mall', name='mall'),
    url(r'^commodity/(?P<id>[0-9]*)/$', 'wafuli.views.commodity', name='commodity_detail'),
    url(r'^press/(?P<id>[0-9]*)/$', 'wafuli.views.press', name='press_detail'),
    url(r'^mallpage/$', 'wafuli.views.get_commodity_page', name='get_commodity_page'),
    # url(r'^financepage/$', 'wafuli.views.get_finance_page', name='get_finance_page'),
    url(r'^financepage/$', 'wafuli.finance.get_finance_page', name='get_finance_page'),   #jzy
    url(r'^taskpage/$', 'wafuli.views.get_task_page', name='get_task_page'),
    url(r'^welpage/$', 'wafuli.views.get_wel_page', name='get_wel_page'),
    url(r'^presspage/$', 'wafuli.views.get_press_page', name='get_press_page'),
    url(r'^aboutus/$', 'wafuli.views.aboutus', name="aboutus"),
#     url(r'^exp_tf/$', 'wafuli.views.experience_taskandfinance', name='exp_tf'),
    url(r'^exp_wel_erweima/$', 'wafuli.welfare.exp_welfare_erweima', name='exp_welfare_erweima'),
    url(r'^exp_wel_openwindow/$', 'wafuli.welfare.exp_welfare_openwindow', name='exp_welfare_openwindow'),
    url(r'^exp_wel_youhuiquan/$', 'wafuli.welfare.exp_welfare_youhuiquan', name='exp_welfare_youhuiquan'),
    url(r'^expsubmit/task/$', 'wafuli.views.expsubmit_task', name='expsubmit_task'),
    url(r'^expsubmit/finance/$', 'wafuli.views.expsubmit_finance', name='expsubmit_finance'),
    url(r'^lookup_order/$', 'wafuli.views.lookup_order', name='lookup_order'),
    url(r'^submit_order/$', 'wafuli.views.submit_order', name='submit_order'),

    url(r'^freshman/introduction/$', TemplateView.as_view(template_name="freshman_introduction.html"), name='freshman_introduction'),
    url(r'^freshman/award/$', TemplateView.as_view(template_name="freshman_award.html"), name='freshman_award'),

    url(r'^activity/recommend/$', 'wafuli.activity.recommend', name='activity_recommend'),
    url(r'^activity/recompage/$', 'wafuli.activity.get_activity_recommend_page', name='get_activity_recommend_page'),
    url(r'^activity/recomrankpage/$', 'wafuli.activity.get_recommend_rank_page', name='get_recommend_rank_page'),

    url(r'^activity/lottery/$', 'wafuli.activity.lottery', name='activity_lottery'),
    url(r'^activity/lottery/get_lottery/$', 'wafuli.activity.get_lottery', name='get_lottery'),

#     url(r'^business/(?:list-page(?P<page>[0-9]*)/)?$', 'wafuli.views.business', name='business_list'),
    url(r'^information/(?:(?P<id>[0-9]*)/)?$', 'wafuli.views.information', name='information'),
    url(r'^information/(?:(?P<type>wahangqing|wagushi|washuju|wahuodong)/)?(?:list-page(?P<page>[0-9]*)/)?$', 'wafuli.views.information', name='information_list'),

    url(r'^sitemap/$', TemplateView.as_view(template_name="sitemap.html"), name='sitemap'),
    url(r'^screenshot/$', 'wafuli.views.display_screenshot', name='screenshot'),

    url(r'^APP_download/$', TemplateView.as_view(template_name="download_app.html"), name='APP_download'),

    url(r'^hongbaolist/$', views.HongbaoList.as_view()),
    url(r'^welfare/(?:(?P<id>[0-9]*)/)?$', views.hongbao, name='welfare'),
    url(r'^updown_welfare/(?:(?P<id>[0-9]*)/)?$', views.updown_hongbao, name='updown_welfare'),

    url(r'^media_submit/$', mediaproject.media_submit, name='media_submit'),
    url(r'^usereventlist/$', rest.UserEventList.as_view()),
    
    url(r'^userevent/(?P<pk>[0-9]+)/$', rest.UserEventDetail.as_view()),
]
