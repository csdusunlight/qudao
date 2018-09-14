import requests

from django.shortcuts import render
from django.http.response import JsonResponse

# Create your views here.

def tpwdtoid(request):
    param = request.get_full_path().split('?')[1]
    res = requests.get('https://api.open.myquan.cc/apiv1/tpwdtoid?'+param, verify=False)
    return JsonResponse(res.json())
def getitemgyurl(request):
    param = request.get_full_path().split('?')[1]
    res = requests.get('https://api.open.myquan.cc/apiv1/getitemgyurl?'+param, verify=False)
    return JsonResponse(res.json())
def getitemgyurlbytpwd(request):
    param = request.get_full_path().split('?')[1]
    res = requests.get('https://api.open.myquan.cc/apiv1/getitemgyurlbytpwd?'+param, verify=False)
    return JsonResponse(res.json())
def gettkorder(request):
    param = request.get_full_path().split('?')[1]
    res = requests.get('https://api.open.myquan.cc/apiv1/gettkorder?'+param, verify=False)
    return JsonResponse(res.json())