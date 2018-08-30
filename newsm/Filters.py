import django_filters
from .models import Tag,Article,Agroup

class TagFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model = Tag
        field=['tname','tslug']
        exclude=['tintro']


class ArticleFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model = Article
        field=['atitle','aslug','atag','acontent']
        exclude=['apic']


class AgroupFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model = Agroup
        field=['aname',]
        exclude=[]