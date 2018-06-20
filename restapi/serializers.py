#coding:utf-8
'''
Created on 2017年8月10日

@author: lch
'''
from rest_framework import serializers
from wafuli.models import Project, InvestLog, TransList, Notice, SubscribeShip,\
    Announcement, WithdrawLog, Mark, BookLog
from account.models import MyUser, ApplyLog, Message,ApplyLogForChannel,ApplyLogForFangdan
from wafuli_admin.models import DayStatis
from wafuli.models import Company
from statistic.models import UserDetailStatis, UserAverageStatis,\
    PerformanceStatistics
# from activity.models import SubmitRank, IPLog
from docs.models import Document

class UserSerializer(serializers.ModelSerializer):
    real_name = serializers.CharField(source="user_bankcard.first.real_name")
    bank = serializers.CharField(source="user_bankcard.first.get_bank_display")
    card_number = serializers.CharField(source="user_bankcard.first.card_number")
    fanshu_domain = serializers.CharField(source="get_fanshu_domain")
    class Meta:
        model = MyUser
        fields = ('id', 'mobile', 'username', 'qq_number', 'qq_name', 'date_joined', 'with_total','accu_income','is_book_email_notice',
                  'level', 'picture', 'profile', 'balance', 'is_active', 'color', 'real_name', 'bank', 'card_number', 'is_autowith',
                  'submit_bg', 'domain_name', 'cs_qq', 'is_merchant','num_message_sync','margin_account', 'fanshu_domain', 'zhifubao','has_permission200')
        read_only_fields = ('id', 'mobile', 'balance', 'is_active', 'level', 'margin_account')

class ApplyLogForChannelSerializer(serializers.ModelSerializer):
    username =serializers.CharField(source="user.username",read_only=True)
    admin_name =serializers.CharField(source="admin_user.username",read_only=True)
    admin_mobile =serializers.CharField(source="admin_user.mobile",read_only=True)

    mobile = serializers.CharField(source="user.mobile",read_only=True)
    qq_number = serializers.CharField(source="user.qq_number",read_only=True)
    qq_name =  serializers.CharField(source="user.qq_name",read_only=True)
    level =  serializers.CharField(source="user.level",read_only=True)
    profile =  serializers.CharField(source="user.profile",read_only=True)
    user_origin = serializers.CharField(source='get_user_origin_display')
    user_exp_year = serializers.CharField(source='get_user_exp_year_display')
    user_custom_volumn = serializers.CharField(source='get_user_custom_volumn_display')
    user_funds_volumn = serializers.CharField(source='get_user_funds_volumn_display')
    user_invest_orientation = serializers.CharField(source='get_user_invest_orientation_display')
    submit_time = serializers.DateTimeField(format= "%Y-%m-%d %H:%M:%S")
    audit_time = serializers.DateTimeField(format= "%Y-%m-%d %H:%M:%S")


    class Meta:
        model = ApplyLogForChannel
        #fields= '__all__'
        fields = ('id',
                  'qq_number',
                  'qq_name',
                  'username',
                  'mobile',
                  'audit_time',
                  'submit_time',
                  'profile',
                  'admin_name',
                  'level',
                  'user_origin',
                  'user_exp_year',
                  'user_custom_volumn',
                  'user_funds_volumn',
                  'user_invest_orientation',
                  'audit_reason',
                  'audit_state',
                  'admin_mobile')
        read_only_fields = ('admin_name','username','qq_number','qq_name')

class ApplyLogForFangdanSerializer(serializers.ModelSerializer):
    username =serializers.CharField(source="user.username",read_only=True)
    admin_name =serializers.CharField(source="admin_user.username",read_only=True)
    admin_mobile =serializers.CharField(source="admin_user.mobile",read_only=True)

    mobile = serializers.CharField(source="user.mobile",read_only=True)
    qq_number = serializers.CharField(source="user.qq_number",read_only=True)
    qq_name =  serializers.CharField(source="user.mobile",read_only=True)
    level =  serializers.CharField(source="user.level",read_only=True)
    profile =  serializers.CharField(source="user.profile",read_only=True)
    audit_time = serializers.DateTimeField(format= "%Y-%m-%d %H:%M:%S")
    submit_time= serializers.DateTimeField(format= "%Y-%m-%d %H:%M:%S")

    class Meta:
        model = ApplyLogForFangdan
        #fields= '__all__'
        fields = ('id',
                  'qq_number',
                  'qq_name',
                  'username',
                  'mobile',
                  'audit_time',
                  'submit_time',
                  'profile',
                  'admin_name',
                  'level',
                  "id_name",
                  "id_num",
                  "apply_pic_url",
                  "contract_pic_url",
                  "rebate_pic_url",
                  'audit_reason',
                  'audit_state',
                  'admin_mobile')
        read_only_fields = ('admin_name','username','qq_number','qq_name')

class ProjectSerializer(serializers.ModelSerializer):
#     subscribers = UserSerializer(many=True)
    qq_name = serializers.CharField(source='user.qq_name', read_only=True)
    user_mobile = serializers.CharField(source='user.mobile', read_only=True)
    state_des = serializers.CharField(source='get_state_display', read_only=True)
    logo = serializers.CharField(source='company.logo.url', read_only=True)
    display_price = serializers.SerializerMethodField()
    up_price = serializers.SerializerMethodField()
    def get_field_names(self, declared_fields, info):
        return serializers.ModelSerializer.get_field_names(self, declared_fields, info)
    def get_display_price(self, obj):
        user = self.context['request'].user
        if user.is_authenticated():
            level = str(user.level)
            return getattr(obj, 'price'+str(level)) or obj.default_price
        else:
            return obj.default_price
    def get_up_price(self, obj):
        user = self.context['request'].user
        if user.is_authenticated() and (user.is_staff or obj.user==user):
            return obj.up_price
        else:
            return ''
    class Meta:
        model = Project
        exclude = ('subscribers', 'price01', 'price02', 'price03', 'price04', 'price05')
#         fields = '__all__'
        read_only_fields = ('user', 'pub_date', 'state', 'is_official', 'category')
        
class InvestLogSerializer(serializers.ModelSerializer):
    project_title = serializers.CharField(source='project.title', read_only=True)
    project_channel = serializers.CharField(source='project.channel', read_only=True)
    cqq_number = serializers.CharField(source='user.qq_number', read_only=True)
    mqq_number = serializers.CharField(source='project.user.qq_number', read_only=True)
    qq_name = serializers.CharField(source='user.qq_name', read_only=True)
    user_level = serializers.CharField(source='user.level', read_only=True)
    user_mobile = serializers.CharField(source='user.mobile', read_only=True)
    audit_state_des = serializers.CharField(source='get_audit_state_display', read_only=True)
    pay_state_des = serializers.CharField(source='get_pay_state_display', read_only=True)
    preaudit_state_des = serializers.CharField(source='get_preaudit_state_display', read_only=True)
    admin_user = serializers.CharField(source='admin_user.username', read_only=True) 
    admin_user = serializers.CharField(source='admin_user.username', read_only=True)
    other_remark = serializers.CharField(source='get_other_and_remark', read_only=True)
    submit_type_des = serializers.CharField(source='get_submit_type_display', read_only=True)
    submit_way_des = serializers.CharField(source='get_submit_way_display', read_only=True)
    project_price = serializers.CharField(source='get_project_price', read_only=True)
    broker_rate = serializers.CharField(source='get_project_broker', read_only=True)
    project_qq_name = serializers.CharField(source='project.user.qq_name', read_only=True)
    class Meta:
        model = InvestLog
        fields = '__all__'
        read_only_fields = ('audit_date','submit_time','user','qq_number','qq_name','user_level','project_price',
                             'user_mobile', 'settle_amount', "admin_user", "is_official",'category')
class TransListSerializer(serializers.ModelSerializer):
    mobile = serializers.CharField(source='user.mobile', read_only=True)
    user_balance = serializers.CharField(source='balance', read_only=True)
    username = serializers.CharField(source='user.qq_number', read_only=True)
    class Meta:
        model = TransList
        fields = '__all__'
        
class NoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = '__all__'
        read_only_fields = ('user', 'time')

class ApplyLogSerializer(serializers.ModelSerializer):
    admin_mobile = serializers.CharField(source='admin_user.mobile')
    class Meta:
        model = ApplyLog
#         fields = '__all__'
        exclude = ('password',)
# SubscribeShip
class SubscribeShipSerializer(serializers.ModelSerializer):
    project_category = serializers.CharField(source='project.category', read_only=True)
    project_channel = serializers.CharField(source='project.channel', read_only=True)
    project_title = serializers.CharField(source='project.title', read_only=True)
    project_intro = serializers.CharField(source='project.introduction', read_only=True)
    project_price = serializers.CharField(source='get_project_price', read_only=True)
    project_cprice = serializers.CharField(source='project.cprice', read_only=True)
    project_shortprice = serializers.CharField(source='project.shortprice', read_only=True)
    project_investrange = serializers.CharField(source='project.investrange', read_only=True)
    project_intrest = serializers.CharField(source='project.intrest', read_only=True)
    project_term = serializers.CharField(source='project.term', read_only=True)
    project_state = serializers.CharField(source='project.state', read_only=True)
    project_strategy = serializers.CharField(source='project.strategy', read_only=True)
    project_introduction = serializers.CharField(source='project.introduction', read_only=True)
    project_picture = serializers.CharField(source='project.picture_url', read_only=True)
    project_marks = serializers.CharField(source='project.marks_list', read_only=True)
    project_is_official = serializers.CharField(source='project.is_official', read_only=True)
    project_remark = serializers.CharField(source='project.remark', read_only=True)
    project_is_book = serializers.BooleanField(source='project.is_book', read_only=True)
    submit_num = serializers.IntegerField(source='project.points', read_only=True)
    necessary_fields = serializers.CharField(source='project.necessary_fields', read_only=True)
    optional_fields = serializers.CharField(source='project.optional_fields', read_only=True)
    project_is_multisub_allowed = serializers.BooleanField(source='project.is_multisub_allowed', read_only=True)
    marks = serializers.StringRelatedField(many=True, read_only=True)
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
class WithdrawLogSerializer(serializers.ModelSerializer):
    real_name = serializers.CharField(source="user.user_bankcard.first.real_name")
    bank = serializers.CharField(source="user.user_bankcard.first.get_bank_display")
    card_number = serializers.CharField(source="user.user_bankcard.first.card_number")
    username = serializers.CharField(source='user.username', read_only=True)
    mobile = serializers.CharField(source='user.mobile', read_only=True)
    admin_mobile = serializers.CharField(source='admin_user.mobile', read_only=True)
    qq_number = serializers.CharField(source='user.qq_number', read_only=True)
    zhifubao = serializers.CharField(source='user.zhifubao', read_only=True)
#     username = serializers.CharField(source='user.username', read_only=True)
#     username = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model = WithdrawLog
        fields = '__all__'
#         read_only_fields = ('audit_time','submit_time','user','audit_state',
#                              'settle_amount','return_amount', "admin_user", "is_official"), 'time', 'content_type', 'object_id', 'user', 'username', 'project')

class UserDetailStatisSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDetailStatis
        fields = '__all__'
class UserAverageStatisSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAverageStatis
        fields = '__all__'
        
class MarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mark
        fields = '__all__'
        
class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'
        
# class RankSerializer(serializers.ModelSerializer):
#     user_pic = serializers.CharField(source='user.picture_url', read_only=True)
#     mobile = serializers.CharField(source='user.get_encrypt_mobile', read_only=True)
#     class Meta:
#         model = SubmitRank
#         fields = '__all__'
#         
# class IPLogSerializer(serializers.ModelSerializer):
#     mobile = serializers.CharField(source='user.mobile', read_only=True)
#     username = serializers.CharField(source='user.username', read_only=True)
#     class Meta:
#         model = IPLog
#         fields = '__all__'
        
class BookLogSerializer(serializers.ModelSerializer):
    state_des = serializers.CharField(source='get_state_display', read_only=True)
    project_title = serializers.CharField(source='project.title', read_only=True)
    class Meta:
        model = BookLog
        fields = '__all__'
        
class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'title', 'content', 'update_time', 'is_on', 'secret', 'is_star','fanshu_url','close_time']
        read_only_fields = ('id',)
        
class MesssageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'
        read_only_fields = ('id',)
        
class PerformStatisSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    inviter_code = serializers.CharField(source='user.invite_code')
    class Meta:
        model = PerformanceStatistics
        fields = '__all__'