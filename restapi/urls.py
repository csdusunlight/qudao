
from django.conf.urls import url, include
from rest_framework import routers

from restapi import views

router = routers.SimpleRouter()
router.register(r'erlei_msgs', views.MsgLogViewSet)
urlpatterns = [
    url(r'^api-auth/', include('rest_framework.urls',namespace='rest_framework')),
    url(r'^projects/$', views.ProjectList.as_view()),
    url(r'^projects/(?P<pk>[0-9]+)/$', views.ProjectDetail.as_view(), kwargs={'partial':True}),
    
    url(r'^users/$', views.UserList.as_view()),
    url(r'^admin_get_apply_user/$', views.ApplyLogForChannelList.as_view()),
    url(r'^admin_get_apply_user_fangdan/$', views.ApplyLogForFangdanList.as_view()),
    url(r'^users/(?P<pk>[0-9]+)/$', views.UserDetail.as_view(), kwargs={'partial':True}),
    
    url(r'^investlogs/$', views.InvestlogList.as_view()),
    url(r'^investlogs/(?P<pk>[0-9]+)/$', views.InvestlogDetail.as_view(), kwargs={'partial':True}),
    
    url(r'^withdrawlogs/$', views.WithdrawLogList.as_view()),
    
    url(r'^translist/$', views.TranslistList.as_view()),
    
    url(r'^notice/$', views.NoticeList.as_view()),
    url(r'^notice/(?P<pk>[0-9]+)/$', views.NoticeDetail.as_view(), kwargs={'partial':True}),
    
    url(r'^announcement/$', views.AnnouncementList.as_view()),
    url(r'^announcement/(?P<pk>[0-9]+)/$', views.AnnouncementDetail.as_view(), kwargs={'partial':True}),
    
    url(r'^sub/$', views.SubscribeShipList.as_view()),
    url(r'^sub/(?P<pk>[0-9]+)/$', views.SubscribeShipDetail.as_view(), kwargs={'partial':True}),
    
    url(r'^daystatis/$', views.DayStatisList.as_view()),
    
    url(r'^applylog/$', views.ApplyLogForChannelList.as_view()),
    
    url(r'^userstatis/$', views.UserDetailStatisList.as_view()),
    url(r'^useravgstatis/$', views.UserAverageStatisList.as_view()),
    
    url(r'^marks/$', views.MarkList.as_view()),
    url(r'^marks/(?P<pk>[0-9]+)/$', views.MarkDetail.as_view()),
    
    url(r'^company/$', views.CompanyList.as_view()),
    url(r'^company2/$', views.CompanyList2.as_view()),
    
#     url(r'^rank/$', views.RankList.as_view()),
    
#     url(r'^iplogs/$', views.IPLogList.as_view()),
    
    url(r'^books/$', views.BookLogList.as_view()),
    url(r'^books/(?P<pk>[0-9]+)/$', views.BookLogDetail.as_view(), kwargs={'partial':True}),
    
    url(r'^docs/$', views.DocumentList.as_view(), ),
    url(r'^docs/(?P<pk>[0-9a-zA-Z]+)/$', views.DocumentDetail.as_view(), kwargs={'partial':True}),
    
#     url(r'^doc/', include_docs_urls(title='d'))
    url(r'^msgs/$', views.MessageList.as_view(), ),
    url(r'^perform/$', views.PerformStatisList.as_view(), ),
    url(r'^msgs/(?P<pk>[0-9]+)/$',views.MessageDetail.as_view(),kwargs={'partial':True}, name='sitemessagedetail'),

    url(r'^msgs/(?P<pk>[0-9]+)/$',views.MessageDetail.as_view(),kwargs={'partial':True}, name='sitemessagedetail'),

]

urlpatterns += router.urls