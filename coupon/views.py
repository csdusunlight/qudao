#coding:utf-8
from django.shortcuts import render, redirect
from rest_framework.generics import ListCreateAPIView
from coupon.serializers import UserCouponSerializer, ContractSerializer
from coupon.models import UserCoupon, Contract
from public.Paginations import MyPageNumberPagination
from public.permissions import CsrfExemptSessionAuthentication
from rest_framework import permissions, generics
from rest_framework.filters import SearchFilter
import django_filters
from public.tools import has_permission, login_required_ajax
from django.http.response import JsonResponse
from django.contrib.auth.decorators import login_required
from account.models import MyUser
from django.views.decorators.csrf import csrf_exempt
import logging
from coupon.Filters import UserCouponFilter
logger = logging.getLogger('wafuli')
# Create your views here.
class BaseViewMixin(object):
    authentication_classes = (CsrfExemptSessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
class ContractList(BaseViewMixin, ListCreateAPIView):
    queryset = Contract.objects.all()
    permission_classes = (permissions.IsAdminUser,)
    serializer_class = ContractSerializer
    filter_backends = (SearchFilter,)
#     filter_class = ApplyProjectFilter
#     ordering_fields = ('state','pub_date','pinyin')
    search_fields = ('name', )
    pagination_class = MyPageNumberPagination
class ContractDetail(BaseViewMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Contract.objects.all()
    permission_classes = (permissions.IsAdminUser,)
    serializer_class = ContractSerializer
class UserCouponList(BaseViewMixin, ListCreateAPIView):
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return UserCoupon.objects.all()
        else:
            return UserCoupon.objects.filter(user=user)
        
    serializer_class = UserCouponSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
#     filter_fields = ['user']
    filter_class = UserCouponFilter
#     ordering_fields = ('state','pub_date','pinyin')
#     search_fields = ('name', )
    pagination_class = MyPageNumberPagination

def on_register(user):
    contracts = Contract.objects.filter(name__startswith=u"新手红包")
    bulks = []
    for con in contracts:
        bulk = UserCoupon(type='heyue', user=user, contract=con, award=con.award)
        bulks.append(bulk)
    bulks.append(UserCoupon(type='guanzhu', user=user, award=1))
    bulks.append(UserCoupon(type='bangka', user=user, award=2))
    bulks.append(UserCoupon(type='shoudan', user=user, award=5))
    UserCoupon.objects.bulk_create(bulks)
    
@csrf_exempt
@login_required_ajax
def open_coupon(request):
    id = request.POST.get('id')
    UserCoupon.objects.get(user=request.user, id=id).open()
    return JsonResponse({'code':0})

@csrf_exempt
@login_required_ajax
def get_coupon_schedule(request):
    id = request.POST.get('id')
    count, amount = UserCoupon.objects.get(user=request.user, id=id).check_schedule()
    return JsonResponse({'count':count, 'amount':amount})