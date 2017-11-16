from django.conf.urls import url
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^doc_list/$', 'docs.views.get_user_doc_list', name='doc_list'),
    url(r'^create_doc/$', 'docs.views.create_doc', name='create_doc'),
    url(r'^update_doc/$', 'docs.views.update_doc', name='update_doc'),
]
