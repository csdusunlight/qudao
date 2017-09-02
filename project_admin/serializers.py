#coding:utf-8
'''
Created on 2017年7月3日

@author: lch
'''
from rest_framework import serializers
from .models import *
class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'
class PlatformSerializer(serializers.ModelSerializer):
#     contacts = serializers.PrimaryKeyRelatedField(many=True, queryset=Contact.objects.all())
    contacts = ContactSerializer(many=True, read_only=True)
    class Meta:
        model = Platform
        fields = ('id', 'name', 'url', 'contacts')
class ProjectSerializer(serializers.ModelSerializer):
    state_des = serializers.CharField(source='get_state_display', read_only=True)
    settleway_des = serializers.CharField(source='get_settleway_display', read_only=True)
    platformname = serializers.CharField(source='platform.name', read_only=True)
    class Meta:
        model = Project
        fields = ('id', 'name', 'platform','platformname','time', 'contact', 'coopway', 'settleway', 'settleway_des', 'state','state_des',
                  'contract_company', 'settle', 'cost', 'cost_explain', 'consume', 'settle_detail',
                  'topay_amount', 'profit', 'finish_time', 'remark')
        read_only_fields = ('id', 'profit','topay_amount','settleway_des','consume','state_des', 'time')

class ProjectInvestDataSerializer(serializers.ModelSerializer):
    projectname = serializers.CharField(source='project.name', read_only=True)
#     projectid = serializers.CharField(source='project.id', read_only=True)
    state_des = serializers.CharField(source='get_state_display', read_only=True)
    source_des = serializers.CharField(source='get_source_display', read_only=True)
    class Meta:
        model = ProjectInvestData
        fields =('id', 'project', 'projectname', 'is_futou','futou_des','invest_mobile','invest_time','invest_amount','source',
                 'invest_term','settle_amount','return_amount','state','audit_time','state_des','remark','source_des')
        read_only_fields = ('id',)

        
class ProjectStatisSerializer(serializers.ModelSerializer):
    projectname = serializers.CharField(source='project.name', read_only=True)
    finish_time = serializers.CharField(source='project.finish_time', read_only=True)
    start_time = serializers.CharField(source='project.time', read_only=True)
    topay_amount = serializers.CharField(source='project.topay_amount', read_only=True)
    state_des = serializers.CharField(source='project.get_state_display', read_only=True)
    class Meta:
        model = ProjectStatis
        fields =('id','project','projectname', 'start_time', 'finish_time', 'topay_amount', 'channel_consume','channel_return','site_consume','site_return',
                 'consume','ret','state_des')
#         read_only_fields = '__all__'

class DayStatisSerializer(serializers.ModelSerializer):
    class Meta:
        model = DayStatis
        fields = '__all__'
        
class AccountSerializer(serializers.ModelSerializer):
    type_des = serializers.CharField(source='get_type_display', read_only=True)
    bank_des = serializers.CharField(source='get_bank_display', read_only=True)
    class Meta:
        model = Account
        fields = ('id','time','type','name','bankaccount','bank','subbranch','balance','remark','type_des','bank_des')
        read_only_fields = ('id',)
class AccountBillSerializer(serializers.ModelSerializer):
    account_type = serializers.CharField(source='account.get_type_display', read_only=True)
    account_name = serializers.CharField(source='account.name', read_only=True)
    account_balance = serializers.CharField(source='account.balance', read_only=True)
    subtype_des = serializers.CharField(source='get_subtype_display', read_only=True)
    type_des = serializers.CharField(source='get_type_display', read_only=True)
#     strftime = serializers.CharField(source='strftime', read_only=True)
    class Meta:
        model = AccountBill
        fields = ('id', 'strftime', 'account', 'type', 'subtype', 'target', 'amount', 'remark',
                  'account_type','account_name','account_balance','subtype_des','type_des')        

class DayAccountStatisSerializer(serializers.ModelSerializer):
    class Meta:
        model = DayAccountStatic
        fields = '__all__'