
from django.conf.urls import url, include
from restapi import views

urlpatterns = [
    url(r'^api-auth/', include('rest_framework.urls',namespace='rest_framework')),
    url(r'^projects/$', views.ProjectList.as_view()),
    url(r'^projects/(?P<pk>[0-9]+)/$', views.ProjectDetail.as_view()),
    
    url(r'^users/$', views.UserList.as_view()),
    url(r'^users/(?P<pk>[0-9]+)/$', views.UserDetail.as_view()),
    
    url(r'^investlogs/$', views.InvestlogList.as_view()),
    url(r'^investlogs/(?P<pk>[0-9]+)/$', views.InvestlogDetail.as_view()),
    
    url(r'^translist/$', views.TranslistList.as_view()),
    
    url(r'^notice/$', views.NoticeList.as_view()),
    url(r'^notice/(?P<pk>[0-9]+)/$', views.NoticeDetail.as_view()),
    
    url(r'^announcement/$', views.AnnouncementList.as_view()),
    url(r'^announcement/(?P<pk>[0-9]+)/$', views.AnnouncementDetail.as_view()),
]
