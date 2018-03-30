from django.conf.urls import url
from django.views.generic.base import TemplateView
from . import views

urlpatterns = [
    url(r'^coupons/$', views.userCouponList.as_view()),
    url(r'^contracts/$', views.contractList.as_view()),
    url(r'^open_coupon/$', views.open_coupon),
]






