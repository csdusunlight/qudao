# -*- coding: utf-8 -*-
from rest_framework import generics, permissions
import django_filters
from public.Paginations import MyPageNumberPagination
from django.shortcuts import render
from django.http import HttpResponse
from .models import Tag, Article,Agroup
from rest_framework import viewsets
from .serializers import TagSerializer,ArticleSerializer,AgroupSerializer
from rest_framework.filters import SearchFilter, OrderingFilter
from .Filters import TagFilter,ArticleFilter,AgroupFilter
from rest_framework.decorators import detail_route,list_route
from rest_framework.response import Response
from django.db.models import Q
from itertools import chain
class TagSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    filter_backends = (SearchFilter, django_filters.rest_framework.DjangoFilterBackend, OrderingFilter)
    filter_class = TagFilter
    pagination_class = MyPageNumberPagination


def get_article_detail(request):
    if request.method == 'GET':
        template = 'account/get_article_detail.html'
        return render(request, template)

def get_article_list(request):
    if request.method == 'GET':
        template = 'account/get_article_list.html'
        return render(request, template)


class ArticleSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class =ArticleSerializer
    filter_class = ArticleFilter
    filter_backends = (SearchFilter, django_filters.rest_framework.DjangoFilterBackend, OrderingFilter)
    pagination_class = MyPageNumberPagination
    ordering_fields = ('ais_hot',
                       'agroup',
                       'atitle',
                       'apub_date',
                       'aupdate_time'
                       )
    ordering=('ais_hot')
    @detail_route(methods=['RETRIEVE'],url_path='lookup_by_tag')
    def lookup_by_tag(self,request,pk=None):

        #输入是一个article,根据article查出tag,根据tag查出对应的article
        aimtag = Article.objects.filter(id=pk)[0]
        tags=aimtag.atag.values_list()
        aimarticle=Article.objects.filter(atag__tname__in=[tags[i][1] for i in range(0,len(tags))]).order_by('-apub_date')
        self.__class__.queryset = aimarticle
        page = self.paginate_queryset(aimarticle)
        returndata = ArticleSerializer(instance=page, many=True)
        return self.get_paginated_response(returndata.data)

    @detail_route(methods=['LIST'],url_path='lookup_by_group')
    def lookup_by_agroup(self,request,**dict):
        para1 = request.GET.get('groupname')
        aimarticle=Article.objects.filter(agroup__agname__exact=para1).order_by('-apub_date')
        self.__class__.queryset = aimarticle
        page = self.paginate_queryset(aimarticle)
        returndata = ArticleSerializer(instance=page, many=True)
        return self.get_paginated_response(returndata.data)


class AgroupSet(viewsets.ModelViewSet):
    queryset = Agroup.objects.all()
    serializer_class =AgroupSerializer
    filter_class = AgroupFilter

from wafuli.models import Project,InvestLog,Company
from restapi.serializers import CompanySerializer
from django.db.models import Count
from django.http import JsonResponse
def get_project_investlog_company(request):
    aimres=InvestLog.objects.values('project__company_id')\
                     .annotate(itemnum=Count('*'))\
                     .values('project__company__name','itemnum','project__company__id')\
                     .order_by('itemnum')
    print(aimres.query)
    aimres = sorted(aimres,key=lambda x:x['itemnum'],reverse=True)[:20]

    #Company.objects.filter(id__in=aimres)
    res={}
    res['code']=0
    res['res']=aimres
    return JsonResponse(res)
