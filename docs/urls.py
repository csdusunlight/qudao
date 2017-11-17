from django.conf.urls import url
from docs import views

urlpatterns = [
    url(r'^list/$', views.get_user_doc_list, name='doc-list'),
    url(r'^create/$', views.create_doc, name='create_doc'),
    url(r'^(?P<id>[0-9]+)/$', views.update_doc, name='update_doc'),
]
