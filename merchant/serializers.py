#coding:utf-8
'''
Created on 2018年1月16日

@author: lch
'''
from rest_framework import serializers
from merchant.models import Apply_Project, Margin_Translog, Margin_AuditLog,\
    MerchantProjectStatistics
class ApplyProjectSerializer(serializers.ModelSerializer):
    pv = serializers.CharField(source="strategy.view_count", read_only=True)
    state_des = serializers.CharField(source="get_audit_state_display", read_only=True)
    strategy_url = serializers.CharField(source="strategy.fanshu_url", read_only=True)
    project_state = serializers.CharField(source="project.state", read_only=True)
    project_state_des = serializers.CharField(source="project.get_state_display", read_only=True)
    user_mobile = serializers.CharField(source="user.mobile", read_only=True)
    qq_number = serializers.CharField(source="user.qq_number", read_only=True)
    qq_name = serializers.CharField(source="user.qq_name", read_only=True)
    class Meta:
        model = Apply_Project
        fields = '__all__'
        read_only_fields = ('user', 'submit_time', 'audit_state', 'audit_user', 'audit_time', 'audit_reason', 'admin_user')
        
class TranslogSerializer(serializers.ModelSerializer):
    mobile = serializers.CharField(source='user.mobile', read_only=True)
    user_margin = serializers.CharField(source='user.margin_account', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model = Margin_Translog
        fields = '__all__'
        
class MarginAuditLogSerializer(serializers.ModelSerializer):
    state_des = serializers.CharField(source="get_audit_state_display", read_only=True)
    margin_account = serializers.CharField(source="user.margin_account")
    username = serializers.CharField(source='user.username', read_only=True)
    mobile = serializers.CharField(source='user.mobile', read_only=True)
    admin_mobile = serializers.CharField(source='admin_user.mobile', read_only=True)
    qq_number = serializers.CharField(source='user.qq_number', read_only=True)
    bank = serializers.CharField(source="user.user_bankcard.first.get_bank_display")
    card_number = serializers.CharField(source="user.user_bankcard.first.card_number")
    real_name = serializers.CharField(source="user.user_bankcard.first.real_name")
    margin_account = serializers.CharField(source='user.margin_account')
    class Meta:
        model = Margin_AuditLog
        fields = '__all__'

class MerchantProjectStatisticsSerializer(serializers.ModelSerializer):
    pv = serializers.CharField(source="view_count", read_only=True)
    project_title = serializers.CharField(source="project.title", read_only=True)
    class Meta:
        model = MerchantProjectStatistics
        fields = '__all__'