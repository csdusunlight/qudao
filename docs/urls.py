from django.conf.urls import url
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^doclist/$', 'account.views.account', name='account_index'),
    url(r'^doclist/$', 'account.views.money', name='account_money'),
    url(r'^yuyue/$', 'account.views.yuyue', name='account_yuyue'),
]
