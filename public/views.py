import time
from qiniu import Auth
from django.conf import settings
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView


access_key = settings.QINIU_AK
secret_key = settings.QINIU_SK


class QiniuTokenView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request):
        q = Auth(access_key, secret_key)
        bucket_name = 'fulitianxia'
        key = 'daniu' + str(int(time.time() * 1000)) + '.jpg'
        token = q.upload_token(bucket_name, key, 3600, {})
        return Response({'token': token, 'code': 0, 'key': key})