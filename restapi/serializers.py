#coding:utf-8
'''
Created on 2017年8月10日

@author: lch
'''
from rest_framework import serializers
from wafuli.models import Project, InvestLog, TransList, Notice, SubscribeShip,\
    Announcement
from account.models import MyUser, ApplyLog
from wafuli_admin.models import DayStatis

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ('id', 'mobile', 'username', 'qq_number', 'qq_name', 'date_joined', 'type',
                  'level', 'picture', 'profile', 'balance', 'is_active', 'color')
        read_only_fields = ('id', 'mobile', 'username', 'balance', 'is_active', 'level', 'type')
        
class ProjectSerializer(serializers.ModelSerializer):
#     subscribers = UserSerializer(many=True)
    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ('user', 'pub_date', 'state', 'is_official')
        
class InvestLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestLog
        fields = '__all__'
        read_only_fields = ('audit_time','submit_time','user','audit_state',
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

class ApplyLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplyLog
#         fields = '__all__'
        exclude = ('password',)
# SubscribeShip
class SubscribeShipSerializer(serializers.ModelSerializer):
    project_source = serializers.CharField(source='project.is_official')
    project_title = serializers.CharField(source='project.title', read_only=True)
    project_intro = serializers.CharField(source='project.introduction', read_only=True)
    project_price01 = serializers.CharField(source='project.price01', read_only=True)
    project_price02 = serializers.CharField(source='project.price02', read_only=True)
    project_price03 = serializers.CharField(source='project.price03', read_only=True)
    project_cprice = serializers.CharField(source='project.cprice', read_only=True)
    project_investrange = serializers.CharField(source='project.investrange', read_only=True)
    project_intrest = serializers.CharField(source='project.intrest', read_only=True)
    project_term = serializers.CharField(source='project.term', read_only=True)
    project_strategy = serializers.CharField(source='project.strategy', read_only=True)
    class Meta:
        model = SubscribeShip
        fields = '__all__'
        read_only_fields = ('user', 'project', 'myprice')
        
class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = '__all__'
        read_only_fields = ('time',)
        
class DayStatisSerializer(serializers.ModelSerializer):
    class Meta:
        model = DayStatis
        fields = '__all__'
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