#coding:utf-8
'''
Created on 2018年3月20日

@author: lch
'''
from rest_framework import serializers
from coupon.models import UserCoupon, Contract
class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = '__all__'
class UserCouponSerializer(serializers.ModelSerializer):
    type_des = serializers.CharField(source='get_type_display', read_only=True)
    state_des = serializers.CharField(source='get_state_display', read_only=True)
    type_des = serializers.CharField(source='get_type_display', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    is_to_expired = serializers.BooleanField(read_only=True)
    class Meta:
        model = UserCoupon
        fields = '__all__'
    