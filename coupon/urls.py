from django.conf.urls import url
from django.views.generic.base import TemplateView
from . import views

urlpatterns = [
    url(r'^coupons/$', views.UserCouponList.as_view()),
    url(r'^contracts/$', views.ContractList.as_view()),
    url(r'^contracts/(?P<pk>[0-9]+)/$', views.ContractDetail.as_view(), kwargs={'partial':True}),
    url(r'^open_coupon/$', views.open_coupon),
    url(r'^get_coupon_schedule/$', views.get_coupon_schedule),
]






