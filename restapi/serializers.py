#coding:utf-8
'''
Created on 2017年8月10日

@author: lch
'''
from rest_framework import serializers
from wafuli.models import Project, InvestLog, TransList, Notice
from account.models import MyUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ('mobile', 'username', 'qq_number', 'qq_name', 'date_joined', 'type',
                  'level', 'picture', 'profile', 'balance', 'is_active')
        read_only_fields = ('mobile', 'username', 'balance', 'is_active', 'level', 'type')
        
class ProjectSerializer(serializers.ModelSerializer):
#     subscribers = UserSerializer(many=True)
    class Meta:
        model = Project
        fields = '__all__'
        
class InvestLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestLog
        fields = '__all__'
        read_only_fields = ('audit_state', 'audit_time',
                             'settle_amount','return_amount', "admin_user", "is_official")
class TransListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransList
        fields = '__all__'
        
class NoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = '__all__'
        read_only_fields = ('user', 'time')
# class MediaProjectSerializer(serializers.ModelSerializer):
#     state_des = serializers.CharField(source='get_state_display', read_only=True)
#     class Meta:
#         model = MediaProject
#         fields = ['id', 'title', 'pub_date', 'state', 'is_vip_bonus', 'is_multisub_allowed',
#                   'is_need_screenshot', 'attention', 'state_des']
#         read_only_fields = ('id', 'pub_date')
# 
# class UserEventSerializer(serializers.ModelSerializer):
#     username = serializers.CharField(source='user.username', read_only=True)
#     mobile = serializers.CharField(source='user.mobile', read_only=True)
#     project = serializers.CharField(source='content_object.title', read_only=True)
#     state_des = serializers.CharField(source='get_audit_state_display', read_only=True)
#     admin_user = serializers.CharField(source='audited_logs.first.user.username')
#     refuse_reason = serializers.CharField(source='audited_logs.first.reason')
#     ret_money = serializers.CharField(source='translist.first.transAmount')
#     ret_score = serializers.CharField(source='score_translist.first.transAmount')
#     class Meta:
#         model = UserEvent
#         fields = '__all__'
#         read_only_fields = ('id', 'audit_state', 'event_type', 'time', 'content_type', 'object_id', 'user', 'username', 'project')