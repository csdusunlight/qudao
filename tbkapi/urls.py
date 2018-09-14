from django.conf.urls import url
from tbkapi import views

urlpatterns = [
    url(r'^getitemgyurl/$', views.getitemgyurl, name='getitemgyurl'),
    url(r'^getitemgyurlbytpwd/$', views.getitemgyurlbytpwd, name='getitemgyurlbytpwd'),
    url(r'^gettkorder/$', views.gettkorder, name='doc_list'),
    url(r'^tpwdtoid/$', views.tpwdtoid, name='tpwdtoid'),
]
