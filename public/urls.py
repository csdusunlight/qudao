from django.conf.urls import url

from public.views import QiniuTokenView

urlpatterns = [
    url(r'^get_upload_token/$', QiniuTokenView.as_view()),
]