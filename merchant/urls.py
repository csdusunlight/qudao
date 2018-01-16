from django.conf.urls import url
from django.views.generic.base import TemplateView
from . import views

urlpatterns = [
#     url(r'^$', 'wafuli_admin.views.index', name='admin_index'),
    url(r'^preaudit_investlog/$', views.preaudit_investlog, name='preaudit_investlog'),
]






