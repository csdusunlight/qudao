#coding:utf-8
'''
Created on 2018年1月16日

@author: lch
'''
from rest_framework import serializers
from merchant.models import Apply_Project, Margin_Translog, Margin_AuditLog
class ApplyProjectSerializer(serializers.ModelSerializer):
    state_des = serializers.CharField(source="get_audit_state_display", read_only=True)
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
    class Meta:
        model = Margin_AuditLog
        fields = '__all__'
