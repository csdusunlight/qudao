from django.conf.urls import url
from docs import views

urlpatterns = [
    url(r'^list/$', views.get_user_doc_list, name='doc-list'),
    url(r'^create/$', views.create_doc, name='create_doc'),
    url(r'^(?P<id>[0-9a-zA-Z]+)/$', views.update_doc, name='update_doc'),
    url(r'^duplicate/(?P<id>[0-9a-zA-Z]+)/$', views.duplicate_doc, name='duplicate_doc'),
]
