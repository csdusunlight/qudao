from rest_framework import serializers
from .models import Tag,Article,Agroup

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

class ArticleSerializer(serializers.ModelSerializer):
    atag = serializers.SerializerMethodField()
    class Meta:
        model = Article
        fields = '__all__'
    def get_atag(self,obj):
        print(obj)
        atag=obj.atag.all()
        data_list=[]
        for row in atag:
            data_list.append({'tname': row.tname})
        return data_list

class AgroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Agroup
        fields = '__all__'
