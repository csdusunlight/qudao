#coding:utf-8
'''
Created on 2018年3月20日

@author: lch
'''
from rest_framework import serializers
from coupon.models import UserCoupon, Contract
class ContractSerializer(serializers.ModelSerializer):
    project_des = serializers.CharField(source='project.title', read_only=True)
    class Meta:
        model = Contract
        fields = '__all__'
class UserCouponSerializer(serializers.ModelSerializer):
    type_des = serializers.CharField(source='get_type_display', read_only=True)
    state_des = serializers.CharField(source='get_state_display', read_only=True)
    type_des = serializers.CharField(source='get_type_display', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    is_to_expired = serializers.BooleanField(read_only=True)
    mobile = serializers.CharField(source='user.mobile', read_only=True)
    qq_name = serializers.CharField(source='user.qq_name', read_only=True)
    contract_name = serializers.CharField(source='contract.name', read_only=True)
    settle_count = serializers.CharField(source='contract.settle_count', read_only=True)
    settle_amount = serializers.CharField(source='contract.settle_amount', read_only=True)
    project_title = serializers.CharField(source='contract.project.title', read_only=True)
    condtype = serializers.CharField(source='contract.condtype', read_only=True)
    class Meta:
        model = UserCoupon
        fields = '__all__'
    