#coding:utf-8
from django.shortcuts import render, get_object_or_404
from django.http.response import Http404
from .models import MyUser, Userlogin,MobileCode
from captcha.views import imageV, generateCap
from account.varify import verifymobilecode, sendmsg_bydhst
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from django.conf import settings
# Avoid shadowing the login() and logout() views below.
from django.contrib.auth import (
    REDIRECT_FIELD_NAME, login as auth_login, authenticate
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm

from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponseRedirect
from django.shortcuts import resolve_url
from django.template.response import TemplateResponse
from django.utils.http import is_safe_url
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
import time as ttime
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Sum, Count
from transaction import charge_money
from account.tools import get_client_ip
from django.db import transaction
from wafuli.data import BANK
from wafuli.models import TransList, WithdrawLog, Project, SubscribeShip,\
    InvestLog, Announcement
from public.tools import login_required_ajax
from wafuli.tools import saveImgAndGenerateUrl
from decimal import Decimal
import re
from weixin.tasks import sendWeixinNotify
from collections import OrderedDict
from django.core.cache import cache
from account.signals import register_signal
from account.models import USER_ORIGIN,USER_EXP_YEAR,USER_CUSTOME_VOLUMN,USER_FUNDS_VOLUMN,USER_INVEST_ORIENTATION
from account.models import ApplyLogForChannel
import datetime
@sensitive_post_parameters()
@csrf_protect
@never_cache
def login(request, template_name='registration/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationForm,
          current_app=None, extra_context=None):
    """
    Displays the login form and handles the login action.
    """
    if request.mobile:
        template_name='registration/m_login.html'
    redirect_to = request.POST.get(redirect_field_name,
                                   request.GET.get(redirect_field_name, ''))
    if request.method == "POST":
        form = authentication_form(request, data=request.POST)
        if form.is_valid():

            # Ensure the user-originating redirection url is safe.
            if not is_safe_url(url=redirect_to, host=request.get_host()):
                redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)

            # Okay, security check complete. Log the user in.
            user = form.get_user()
            logger.info(user.mobile)
            auth_login(request, user)
            # anything you can add here
#             user.last_login_time = user.this_login_time
#             user.this_login_time = datetime.now()
            Userlogin.objects.create(user=user,)
#             user.save(update_fields=["last_login_time", "this_login_time"])
            return HttpResponseRedirect(redirect_to)
        else:
            errors = form.errors
            form.error_msg = u'用户名或密码输入有误'     
            if '__all__' in errors:
                dic = errors['__all__'].get_json_data()
                if dic[0]['code'] == 'invalid_login':
                    form.error_msg = u'用户名或密码输入有误'
                elif dic[0]['code'] == 'inactive':
                    form.error_msg = u'账户行为异常，请联系管理员'            
    else:
        form = authentication_form(request)

    current_site = get_current_site(request)

    context = {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
    }
    if extra_context is not None:
        context.update(extra_context)

    if current_app is not None:
        request.current_app = current_app

    return TemplateResponse(request, template_name, context)
import logging
logger = logging.getLogger('wafuli')

@csrf_exempt
def register(request):
    if request.method == 'POST':
        if not request.is_ajax():
            raise Http404
        result = {}
        telcode = request.POST.get('code', None)
        mobile = request.POST.get('mobile', None)
        password = request.POST.get('password', None)
        qq_number = request.POST.get('qq_number', None)
        qq_name = request.POST.get('qq_name', '')
        invite_code = request.POST.get('invite_code', '')
        if not (telcode and mobile and password and qq_number and qq_name):
            result['code'] = '3'
            result['msg'] = u'传入参数不足！'
            return JsonResponse(result)
        if MyUser.objects.filter(mobile=mobile).exists():
            result['code'] = '1'
            result['msg'] = u'该手机号码已被别人注册过了'
            return JsonResponse(result)
        ret = verifymobilecode(mobile,telcode)
        if ret != 0:
            result['code'] = '2'
            if ret == -1:
                result['msg'] = u'请先获取手机验证码'
            elif ret == 1:
                result['msg'] = u'手机验证码输入错误！'
            elif ret == 2:
                result['msg'] = u'手机验证码已过期，请重新获取'
            return JsonResponse(result)
        
        inviter = None
        if invite_code:
            try:
                inviter = MyUser.objects.get(invite_code=invite_code, is_staff=True)
            except MyUser.DoesNotExist:
                result['code'] = '2'
                result['msg'] = u'该邀请码不存在，请与工作人员联系'
                return JsonResponse(result)
            
        level = '05'
        username = 'flm' + str(mobile)
        with transaction.atomic():
            user = MyUser(mobile=mobile, username=username, level=level, qq_name=qq_name, qq_number=qq_number, inviter=inviter,
                          cs_qq=qq_number, domain_name=qq_number)
            user.set_password(password)
            user.save()
            id_list_list= list(Project.objects.filter(is_official=True, state='10', is_addedto_repo=True).values_list('id'))
            id_list = []
            if id_list_list:
                id_list = reduce(lambda x,y: x + y, id_list_list)
            subbulk = []
            for id in id_list:
                sub = SubscribeShip(user=user, project_id=id)
                subbulk.append(sub)
            SubscribeShip.objects.bulk_create(subbulk)
            register_signal.send('register', user=user)
            try:
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                auth_login(request, user)
                user.last_login = datetime.datetime.now()
                user.save(update_fields=['last_login'])
                Userlogin.objects.create(user=user)
            except:
                pass
#         imgurl_list = []
#         if len(request.FILES)>6:
#             result = {'code':-2, 'msg':u"上传图片数量不能超过6张"}
#             apply.delete()
#             return JsonResponse(result)
#         for key in request.FILES:
#             block = request.FILES[key]
#             if block.size > 100*1024:
#                 result = {'code':-1, 'msg':u"每张图片大小不能超过100k，请重新上传"}
#                 apply.delete()
#                 return JsonResponse(result)
#         for key in request.FILES:
#             block = request.FILES[key]
#             imgurl = saveImgAndGenerateUrl(key, block, 'qualification')
#             imgurl_list.append(imgurl)
#         invest_image = ';'.join(imgurl_list)
#         apply.qualification = invest_image
#         apply.save(update_fields=['qualification',])
        result['code'] = 0
        return JsonResponse(result)
    else:
        mobile = request.GET.get('mobile','')
        icode = request.GET.get('icode','')
        context = {
            'icode':icode,
            'mobile':mobile,
        }
        template = 'registration/m_register.html' if request.mobile else 'registration/register.html'
        return render(request,template, context)

@csrf_exempt
def register_from_gzh(request):
    if request.method == 'POST':
        if not request.is_ajax():
            raise Http404
        result = {}
        password = request.POST.get('password', None)
        qq_number = request.POST.get('qq_number', None)
        qq_name = request.POST.get('qq_name', '')
        profile = request.POST.get('profile', '')
        mobile = request.session.get('mobile')
        invite_code = request.POST.get('invite_code', '')
        if not (mobile and password and qq_number and qq_name):
            result['code'] = '3'
            result['msg'] = u'传入参数不足！'
            return JsonResponse(result)
        if MyUser.objects.filter(mobile=mobile).exists():
            result['code'] = '1'
            result['msg'] = u'该手机号码已被别人注册过了'
            return JsonResponse(result)
        inviter = None
        if invite_code:
            try:
                inviter = MyUser.objects.get(invite_code=invite_code, is_staff=True)
            except MyUser.DoesNotExist:
                result['code'] = '2'
                result['msg'] = u'该邀请码不存在，请与工作人员联系'
                return JsonResponse(result)
            
        level = '05'
        username = 'wx' + str(mobile)
        with transaction.atomic():
            user = MyUser(mobile=mobile, username=username, level=level, qq_name=qq_name, qq_number=qq_number, inviter=inviter,
                          cs_qq=qq_number, domain_name=qq_number)
            user.set_password(password)
            user.save()
            id_list_list= list(Project.objects.filter(is_official=True, state='10', is_addedto_repo=True).values_list('id'))
            id_list = []
            if id_list_list:
                id_list = reduce(lambda x,y: x + y, id_list_list)
            subbulk = []
            for id in id_list:
                sub = SubscribeShip(user=user, project_id=id)
                subbulk.append(sub)
            SubscribeShip.objects.bulk_create(subbulk)
            register_signal.send('register', user=user)
        result['code'] = 0
        return JsonResponse(result)
    else:
        mobile = request.GET.get('mobile','')
        icode = request.GET.get('icode','')
        context = {
            'icode':icode,
            'mobile':mobile,
        }
        template = 'registration/m_register_from_gzh.html'
        return render(request,template, context)

import time
@csrf_exempt
def apply_for_channel_user(request):
    if request.method == 'GET':
        template = 'account/apply_for_channel_user.html'
        return render(request, template)
    if request.method == 'POST':
        #if not request.is_ajax():
        #    raise Http404
        result = {}
        current_user=request.user
        user_origin = request.POST.get('origin', None)
        user_exp_year = request.POST.get('exp_year', None)
        user_custom_volumn = request.POST.get('custom_volumn', None)
        user_funds_volumn = request.POST.get('funds_volumn', None)
        user_invest_orientation = request.POST.get('invest_orientation', None)
            #所有字段的传入内容都是合法的，那么设置
            #写入数据库，设置待审核状态，发送站内消息和短信
        #######################
        def para_check_in_model_choice(para,choices):
            return para in [i[0] for i in choices]
        #######################
        if all([para_check_in_model_choice(user_origin,USER_ORIGIN), \
                para_check_in_model_choice(user_exp_year, USER_EXP_YEAR), \
                para_check_in_model_choice(user_custom_volumn, USER_CUSTOME_VOLUMN), \
                para_check_in_model_choice(user_funds_volumn, USER_FUNDS_VOLUMN),\
                para_check_in_model_choice(user_invest_orientation, USER_INVEST_ORIENTATION)]):
            ApplyLogForChannel.objects.create(user=current_user,
                                      user_origin=user_origin,
                                      user_exp_year=user_exp_year,
                                      user_custom_volumn=user_custom_volumn,
                                      user_funds_volumn=user_funds_volumn,
                                      user_invest_orientation=user_invest_orientation,
                                      audit_state='1')
            current_user.is_channel = '-1'
            current_user.save(update_fields=[
                                             'is_channel',
                                        ])
            result['code'] = 0
            return JsonResponse(result)

        else:
            result['code'] = '3'
            result['msg'] = u'传入参数不合法！'
            return JsonResponse(result)
    else:
        return render(request,"apply_for_channel_user.html")


def verifymobile(request):# not exist  return 0  exist return 1
    mobilev = request.GET.get('mobile', None)
    users = None
    print(mobilev)
    code = '1' # is used
    if mobilev:
        users = MyUser.objects.filter(mobile=mobilev)
        if not users.exists():
            code = '0'
    result = {'code':code,}
    return JsonResponse(result)
def verifyusername(request):
    namev = request.GET.get('username', None)
    users = None
    code = '1' # is used
    if namev:
        users = MyUser.objects.filter(username=namev)
        if not users.exists():
            code = '0'
    result = {'code':code,}
    return JsonResponse(result)
def verifyqq(request):
    qqv = request.GET.get('qq_number', None)
    users = None
    code = '1' # is used
    if qqv:
        users = MyUser.objects.filter(qq_number=qqv)
        if not users.exists():
            code = '0'
    result = {'code':code}
    return JsonResponse(result)
def verifyinviter(request):
    invite_code = request.GET.get('invite_code', None)
    code = '1' # not exist
    if invite_code:
        users = MyUser.objects.filter(invite_code=invite_code)
        if users.exists():
            code = '0'
    result = {'code':code,'msg':'该邀请码不存在，请联系客服索取'}
    return JsonResponse(result)
@login_required
def verify_domainName(request):
    ret = {}
    domain_name = request.GET.get('domain_name', None)
    if not domain_name:
        raise Http404
    if MyUser.objects.filter(domain_name=domain_name).exists():
        if request.user.domain_name == domain_name:
            ret['code'] = 0
        else:
            ret['code'] = 1
            ret['msg'] = u"该域名已被占用"
    else:
        mat = re.match(r'[0-9a-zA-A\-_]+$', domain_name)
        if not mat:
            ret['code'] = 2
            ret['msg'] = u"域名只能包含数字、字母、-和_"
        else:
            ret['code'] = 0
    return JsonResponse(ret)
@csrf_exempt
def callbackby189(request):
    rand_code = request.POST.get('rand_code', None)
    identifier = request.POST.get('identifier', None)
    code = '0' # is used
    if not rand_code or not identifier:
        logger.error('where is it???')
        code = '1'
    else:
        try:
            MobileCode.objects.create(identifier=identifier, rand_code=rand_code)
        except:
            code = '1'
        else:
            code = '0'
    result = {'res_code':code,}
    return JsonResponse(result)

def phoneImageV(request):
#     if not request.is_ajax():
#         raise Http404
    action = request.GET.get('action', None)
    result = {'code':'2',}
    phone = request.GET.get('phone', None)
    if action=='register':
#         hashkey = request.GET.get('hashkey', None)
#         response = request.GET.get('response', None)
#        if not (phone and hashkey and response):
#             raise Http404
#         ret = imageV(hashkey, response)
#         if ret != 0:
#             result['message'] = u'图形验证码输入错误！'
#             result.update(generateCap())
#             return JsonResponse(result)
        users = MyUser.objects.filter(mobile=phone)
        if users.exists():
            result['message'] = u'该手机号码已申请！'
            result.update(generateCap())
            return JsonResponse(result)
    elif action=='forgot_passwd' or action=='reset_password':
        hashkey = request.GET.get('hashkey', None)
        response = request.GET.get('response', None)
        if not (phone and hashkey):
            return JsonResponse(result)
        ret = imageV(hashkey, response)
        if ret != 0:
            result['code'] = 1
            result['message'] = u'图形验证码输入错误！'
            result.update(generateCap())
            return JsonResponse(result)
        users = MyUser.objects.filter(mobile=phone)
        if not users.exists():
            result['code'] = 1
            result['message'] = u'该手机号码尚未注册！'
            result.update(generateCap())
            return JsonResponse(result)
    elif action=="change_bankcard":
        if not request.user.is_authenticated():
            result['code'] = 1
            result['message'] = u"尚未登录"
            return JsonResponse(result)
        phone = request.user.mobile
    stamp = str(phone)
    lasttime = request.session.get(stamp, None)
    now = int(ttime.time())
    if lasttime:
        dif = now - int(lasttime)
        if dif < 60:
            result['message'] = u'请不要频繁提交！'
            result.update(generateCap())
            return JsonResponse(result)
    today = datetime.date.today()
    remote_ip = get_client_ip(request)
    count_ip = MobileCode.objects.filter(remote_ip=remote_ip, create_at__gt=today).count()
    if count_ip >= 30:
        result['message'] = u'该IP当日发送短信请求已超上限，请明日再来！'
        return JsonResponse(result)
    count_mobile = MobileCode.objects.filter(mobile=phone, create_at__gt=today).count()
    if count_mobile >= 5:
        result['message'] = u'该手机号当日短信发送请求已超上限，请明日再来！'
        return JsonResponse(result)
    ret = sendmsg_bydhst(phone)
    if ret:
        logger.info('Varifing code has been send to:' + phone)
        result['code'] = 0
        result['message'] = u"发送验证码成功！"
        MobileCode.objects.create(mobile=phone,rand_code=ret,remote_ip=remote_ip)
        request.session[stamp] = now
    else:
        logger.error('Sending Varifing code to ' + phone + ' is failed!!!')
        result['message'] = u"发送验证码失败！"
    return JsonResponse(result)

@login_required
def account(request):
    announce_list = Announcement.objects.all()
    recom_projects = Project.objects.filter(state='10', is_official=True, is_addedto_repo=True)[0:4]
    template = 'account/m_account_index.html' if request.mobile else 'account/account_index.html'
    return render(request, template,{'announce_list':announce_list, 'recom_projects':recom_projects})
@login_required
def hongbao(request):   #jzy
    template = 'account/m_account_hongbao.html' if request.mobile else 'account/account_hongbao.html'
    return render(request, template,{})

@login_required
def account_setting(request):
    return render(request, 'account/account_setting.html',)

@login_required
def account_notice(request):
    return render(request, 'account/account_notice.html',)

@login_required
def account_submit(request):
    plist = list(Project.objects.filter(state__in=['10','20'], is_official=True))    #jzy
    return render(request, 'account/account_submit.html', {'plist':plist})

@login_required
def account_audited(request):
    user = request.user
    today = datetime.date.today()
    submit_num = InvestLog.objects.filter(user=user, submit_time__gte=today).count()
    nums = InvestLog.objects.filter(user=user, audit_time__gte=today).values('audit_state')\
        .annotate(count=Count('*')).order_by('audit_state')
    kwarg = {'submit_num':submit_num, 'pass_num':0, 'refuse_num':0, 'check_num':0}
    for num in nums:
        state = num.get('audit_state')
        if state=='0':
            kwarg.update(pass_num=num.get('count') or 0)
        elif state=='2':
            kwarg.update(refuse_num=num.get('count') or 0)
        elif state=='3':
            kwarg.update(check_num=num.get('count') or 0)
    appeal_num = InvestLog.objects.filter(user=user, audit_state='4').count() or ''
    except_num = InvestLog.objects.filter(user=user, audit_state='3').count() or ''
    kwarg.update(appeal_num=appeal_num, except_num=except_num)
    template = 'account/m_account_audited.html' if request.mobile else 'account/account_audited.html' 
    return render(request, template, kwarg)

@login_required
def account_audited_2(request):
    user = request.user
    today = datetime.date.today()
    submit_num = InvestLog.objects.filter(user=user, submit_time__gte=today).count()
    nums = InvestLog.objects.filter(user=user, audit_time__gte=today).values('audit_state')\
        .annotate(count=Count('*')).order_by('audit_state')
    kwarg = {'submit_num':submit_num, 'pass_num':0, 'refuse_num':0, 'check_num':0}
    for num in nums:
        state = num.get('audit_state')
        if state=='0':
            kwarg.update(pass_num=num.get('count') or 0)
        elif state=='2':
            kwarg.update(refuse_num=num.get('count') or 0)
        elif state=='3':
            kwarg.update(check_num=num.get('count') or 0)
    template = 'account/m_account_audited_2.html' if request.mobile else 'account/account_audited.html' 
    return render(request, template, kwarg)



# def signin(request):
#
#     if not request.is_ajax():
#         raise Http404
#
#     result={'code':-1, 'url':''}
#     if not request.user.is_authenticated():
#         result['code'] = -1
#         result['url'] = reverse('login') + "?next=" + reverse('account_index')
#     else:
#         signin_last = UserSignIn.objects.filter(user=request.user).first()
#         if signin_last and signin_last.date == date.today():
#             result['code'] = 1
#         else:
#             signed_conse_days = 1
#             if signin_last and signin_last.date == date.today() - timedelta(days=1):
#                 signed_conse_days += signin_last.signed_conse_days
#             UserSignIn.objects.create(user=request.user, date=date.today(), signed_conse_days=signed_conse_days)
#             charge_score(request.user, '0', 5, u"签到奖励")
#             if signed_conse_days%7 == 0:
#                 charge_score(request.user, '0', 20, u"连续签到7天奖励")
#             result['code'] = 0
#     return JsonResponse(result)


@login_required
def security(request):
    return render(request, 'account/account_security.html', {})
@login_required
def message(request):
    #减同步消息的逻辑,在用户打开消息界面的时候将新消息减０了。
    current_user=request.user
    current_user.num_message_sync=0
    current_user.save(update_fields=['num_message_sync',])
    template = 'account/m_account_message.html' if request.mobile else 'account/account_message.html'
    return render(request, template)

def password_change(request):
    if not request.is_ajax():
        raise Http404
    result={'code':-1, 'url':'asd'}
    if not request.user.is_authenticated():
        result['code'] = 1
        result['url'] = reverse('login') + "?next=" + reverse('account_security')
        return JsonResponse(result)
    init_password = request.POST.get("initp", '')
    new_password = request.POST.get("newp", '')
    if not (init_password and new_password):
        result['code'] = -1
        return JsonResponse(result)
    user = request.user
    if not user.check_password(init_password):
        result['code'] = 2
    else:
        user.set_password(new_password)
        user.save(update_fields=["password"])
        result['code'] = 0
    return JsonResponse(result)
def change_pay_password(request):
    if not request.is_ajax():
        raise Http404
    result={'code':-1, 'url':'asd'}
    if not request.user.is_authenticated():
        result['code'] = 1
        result['url'] = reverse('login') + "?next=" + reverse('account_security')
        return JsonResponse(result)
    init_password = request.POST.get("initp", '')
    new_password = request.POST.get("newp", '')
    type = request.POST.get("type", '')
    if not (init_password and new_password and type):
        result['code'] = -1
        return JsonResponse(result)
    user = request.user
    vari = False
    if type == 'set':
        vari = user.check_password(init_password)
    elif type == 'change':
        vari = user.check_pay_password(init_password)
    if vari:
        user.set_pay_password(new_password)
        user.save(update_fields=["pay_password"])
        result['code'] = 0
    else:
        result['code'] = 2
    return JsonResponse(result)

@login_required_ajax
def bind_bankcard(request):
    result={'code':-1, 'url':''}
    if not request.is_ajax():
        raise Http404
    user = request.user
    if request.method == 'POST':
        card_number = request.POST.get("card_number", '')
        real_name = request.POST.get("real_name", '')
        bank = request.POST.get("bank", '')
        subbranch = request.POST.get("subbranch",'')
        telcode = request.POST.get("code", '')
        ret = verifymobilecode(user.mobile,telcode)
        if ret != 0:
            result['code'] = '2'
            if ret == -1:
                result['res_msg'] = u'请先获取手机验证码'
            elif ret == 1:
                result['res_msg'] = u'手机验证码输入错误！'
            elif ret == 2:
                result['res_msg'] = u'手机验证码已过期，请重新获取'
            return JsonResponse(result)
        card = user.user_bankcard.first()
        card.card_number = card_number
        card.real_name = real_name
        card.bank = bank
        card.subbranch = subbranch
        card.save()
        result['code'] = 0
    elif request.method == 'GET':
        if user.user_bankcard.exists():
            raise Http404
        card_number = request.GET.get("card_number", '')
        real_name = request.GET.get("real_name", '')
        bank = request.GET.get("bank", '')
        subbranch = request.GET.get("subbranch",'')
        if card_number and real_name and bank:
            user.user_bankcard.create(user=user, card_number=card_number, real_name=real_name,
                                       bank=bank, subbranch=subbranch)
        #红包活动插入++++++++++
        coupons = user.usercoupons.filter(type='bangka')
        for coupon in coupons:
            coupon.checklock()
        #红包活动插入++++++++++
        result['code'] = 0
    return JsonResponse(result)

@login_required
def m_bind_bankcard_page(request):
    banks = BANK
    template = 'account/m_account_bind_bankcard.html' 
    return render(request, template, {'banks':banks})

@login_required
def m_change_bankcard_page(request):
    banks = BANK
    return render(request, 'account/m_account_change_bankcard.html', {'banks':banks})
@login_required
def m_bind_zhifubao_page(request):
    return render(request, 'account/m_account_bind_zhifubao.html')
@login_required
def m_change_zhifubao_page(request):
    return render(request, 'account/m_account_change_zhifubao.html')

@csrf_exempt
@transaction.atomic
@login_required_ajax
def bind_zhifubao(request):
    result={'code':-1}
    if not request.is_ajax():
        raise Http404
    user = request.user
    zhifubao = request.POST.get('zhifubao', '')
    zhifubao_real_name = request.POST.get("zhifubao_real_name", '')
    telcode = request.POST.get("code", '')
    if user.zhifubao != '':
        ret = verifymobilecode(user.mobile,telcode)
        if ret != 0:
            result['code'] = '2'
            if ret == -1:
                result['res_msg'] = u'请先获取手机验证码'
            elif ret == 1:
                result['res_msg'] = u'手机验证码输入错误！'
            elif ret == 2:
                result['res_msg'] = u'手机验证码已过期，请重新获取'
            return JsonResponse(result)
    user.zhifubao = zhifubao
    user.zhifubao_real_name = zhifubao_real_name
    user.save(update_fields=['zhifubao', 'zhifubao_real_name'])
    result['code'] = 0
    return JsonResponse(result)

@login_required
def money(request):
    template = 'account/m_money.html' if request.mobile else 'account/money.html'
    return render(request, template)
@login_required
def yuyue(request):
    return render(request, 'account/yuyue.html', {})
def get_user_money_page(request):
    user = request.user
    res={'code':0,}
    if not user.is_authenticated():
        res['code'] = -1
        res['url'] = reverse('login') + "?next=" + reverse('account_money')
        return JsonResponse(res)
    page = request.GET.get("page", None)
    size = request.GET.get("size", 10)
    filter = request.GET.get("filter",0)
    try:
        size = int(size)
    except ValueError:
        size = 10
    try:
        filter = int(filter)
    except ValueError:
        filter = 0
    if not page or size <= 0 or filter < 0 or filter > 3:
        raise Http404
    item_list = []

    item_list = TransList.objects.filter(user=request.user)
    if filter == 0:
        item_list = item_list.filter(transType='0')
    elif filter == 1:
        item_list = item_list.filter(transType='1')
    paginator = Paginator(item_list, size)
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
    # If page is not an integer, deliver first page.
        contacts = paginator.page(1)
    except EmptyPage:
    # If page is out of range (e.g. 9999), deliver last page of results.
        contacts = paginator.page(paginator.num_pages)
    data = []
    for con in contacts:
        state = ''
        reason = ''
        state_int=''
        if filter ==1:
            event = con.user_event
            if event:
                state = event.get_audit_state_display()
                state_int = event.audit_state
                if state_int=='2':
                    reason = event.audited_logs.first().reason

        i = {"item":con.reason,
             "amount":con.transAmount,
             "time":con.time.strftime("%Y-%m-%d %H:%M:%S"),
             "remark":con.remark,
             "state":state,
             "state_int":state_int,
             "reason":reason,
             }
        data.append(i)
    if data:
        res['code'] = 1
    res["pageCount"] = paginator.num_pages
    res["recordCount"] = item_list.count()
    res["data"] = data
    return JsonResponse(res)

@login_required
def withdraw(request):
    if request.method == 'GET':
        user = request.user
        card = user.user_bankcard.first()
        template = 'account/m_withdraw.html' if request.mobile else 'account/withdraw.html'
        banks = BANK
        return render(request, template,{"card":card, "banks":banks})
    elif request.method == 'POST':
        user = request.user
        result = {'code':-1, 'res_msg':''}
        withdraw_amount = request.POST.get("amount", None)
        if not withdraw_amount:
            result['code'] = 3
            result['res_msg'] = u'传入参数不足！'
            return JsonResponse(result)
        try:
            withdraw_amount = Decimal(withdraw_amount)
        except ValueError:
            result['code'] = -1
            result['res_msg'] = u'参数不合法！'
            return JsonResponse(result)
        if withdraw_amount < 10 or withdraw_amount > user.balance:
            result['code'] = -1
            result['res_msg'] = u'提现金额错误！'
            return JsonResponse(result)
        # if not user.zhifubao or not user.zhifubao_name:
        #     result['code'] = -1
        #     result['res_msg'] = u'请先绑定支付宝！'
        #     return JsonResponse(result)
        if withdraw_amount >= 50000:
            card = user.user_bankcard.first()
            if not card:
                result['code'] = -1
                result['res_msg'] = u'请先绑定银行卡！'
                return JsonResponse(result)
        elif user.zhifubao == '':
            result['code'] = -1
            result['res_msg'] = u'请先绑定支付宝账号！'
            return JsonResponse(result)
        try:
            with transaction.atomic():
                event = WithdrawLog.objects.create(user=user, amount=withdraw_amount, audit_state='1')
                translist = charge_money(user, '1', withdraw_amount, u'提现', auditlog=event)
                result['code'] = 0
            try:
                sendWeixinNotify.delay([(request.user, event),], 'withdraw_apply')
            except Exception, e:
                logger.error(e)
        except:
            result['code'] = -2
            result['res_msg'] = u'提现失败！'
        return JsonResponse(result)





# @login_required
# def invite(request):
#     inviter = request.user
#     if request.method == 'GET':
#         withdraw_thismonth = UserEvent.objects.filter(user__inviter=inviter, event_type='2',
#                     audit_state='0',audit_time__year=ttime.localtime()[0],audit_time__month=ttime.localtime()[1]).\
#                     aggregate(sumofwith=Sum('invest_amount'))
#         acc_count = inviter.invitees.count()
#         acc_with_count = UserEvent.objects.filter(user__inviter=inviter, event_type='2',
#                     audit_state='0').values('user__mobile').distinct().order_by().count()
#         this_month_award = float(withdraw_thismonth.get('sumofwith') or 0)*settings.AWARD_RATE
#         this_month_award = int(this_month_award)
#         statis = {
#             'left_award':inviter.invite_account,
#             'accu_invite_award':inviter.invite_income,
#             'accu_invite_scores':inviter.invite_scores,
#             'acc_count':acc_count,
#             'acc_with_count':acc_with_count,
#             'this_month_award':this_month_award,
#         }
#         return render(request,'account/account_invite.html', {'statis':statis})
#     elif request.method == 'POST':
#         result = {'code':-1, 'res_msg':''}
#         left_award = inviter.invite_account
#         if left_award == 0:
#             result['res_msg'] = u'邀请奖励结余为0'
#         else:
#             translist = charge_money(inviter, '0', left_award, u'邀请奖励')
#             if translist:
#                 inviter.invite_account = 0
#                 inviter.save(update_fields=['invite_account'])
#                 event = UserEvent.objects.create(user=inviter, event_type='5',
#                             invest_amount=left_award, audit_state='1')
#                 translist.user_event = event
#                 translist.save(update_fields=['user_event'])
#                 result['code'] = 0
#             else:
#                 result['code'] = -2
#                 result['res_msg'] = u'操作失败，请联系客服！'
#         print result
#         return JsonResponse(result)
#
# def get_user_invite_page(request):
#     if not request.is_ajax():
#         raise Http404
#     user = request.user
#     res={'code':0,}
#     if not user.is_authenticated():
#         res['code'] = -1
#         res['url'] = reverse('login') + "?next=" + reverse('account_invite')
#         return JsonResponse(res)
#     page = request.GET.get("page", None)
#     size = request.GET.get("size", 6)
#     filter = request.GET.get("filter",0)
#     try:
#         size = int(size)
#     except ValueError:
#         size = 6
#     try:
#         filter = int(filter)
#     except ValueError:
#         filter = 0
#     if not page or size <= 0 or filter < 0 or filter > 2:
#         raise Http404
#
#     data = []
#     if filter == 0:
#         invitees = user.invitees.all()
#         paginator = Paginator(invitees, size)
#         try:
#             contacts = paginator.page(page)
#         except PageNotAnInteger:
#         # If page is not an integer, deliver first page.
#             contacts = paginator.page(1)
#         except EmptyPage:
#         # If page is out of range (e.g. 9999), deliver last page of results.
#             contacts = paginator.page(paginator.num_pages)
#         for con in contacts:
#             reg = UserEvent.objects.filter(user=con, event_type='2',audit_state='0').exists()
#             mobile = con.mobile
#             if len(mobile)==11:
#                 mobile = mobile[0:3] + '****' + mobile[7:]
#             i = {
#                  "mobile":mobile,
#                  "time":con.date_joined.strftime("%Y-%m-%d %H:%M"),
#                  "is_bind":u'是' if con.user_bankcard else u'否',
#                  "is_with":u'是' if reg else u'否',
#              }
#             data.append(i)
#         if data:
#             res['code'] = 1
#         res["pageCount"] = paginator.num_pages
#         res["recordCount"] = invitees.count()
#     elif filter == 1:
#         events = UserEvent.objects.filter(user__inviter=user, event_type='2', audit_state='0')
#         paginator = Paginator(events, size)
#         try:
#             contacts = paginator.page(page)
#         except PageNotAnInteger:
#         # If page is not an integer, deliver first page.
#             contacts = paginator.page(1)
#         except EmptyPage:
#         # If page is out of range (e.g. 9999), deliver last page of results.
#             contacts = paginator.page(paginator.num_pages)
#         for con in contacts:
#             take_award = float(con.invest_amount)*settings.AWARD_RATE
#             take_award = int(take_award)
#             i = {
#                  "mobile":con.user.mobile,
#                  "time":con.audit_time.strftime("%Y-%m-%d %H:%M"),
#                  "amount":con.invest_amount,
#                  "take":take_award,
#              }
#             data.append(i)
#         if data:
#             res['code'] = 1
#         res["pageCount"] = paginator.num_pages
#         res["recordCount"] = events.count()
#     elif filter == 2:
#         select = {'month': connection.ops.date_trunc_sql('month', 'time')}
#         withdraw_list = UserEvent.objects.filter(user__inviter=user, event_type='2',
#                 audit_state='0',).extra(select=select)\
#                 .values('month').annotate(cou=Count('user',distinct=True),sumofwith=Sum('invest_amount')).order_by('-month',)
#         paginator = Paginator(withdraw_list, size)
#
#         try:
#             contacts = paginator.page(page)
#         except PageNotAnInteger:
#         # If page is not an integer, deliver first page.
#             contacts = paginator.page(1)
#         except EmptyPage:
#         # If page is out of range (e.g. 9999), deliver last page of results.
#             contacts = paginator.page(paginator.num_pages)
#         for con in contacts:
#             take_award = float(con['sumofwith'] or 0)*settings.AWARD_RATE
#             take_award = int(take_award)
#             i = {
#                  "month":str(con['month'])[0:7],
#                  "amount":con['sumofwith'] or 0,
#                  "cou":con['cou'],
#                  "take":take_award,
#                  "score":con['cou']*100,
#              }
#             data.append(i)
#         if data:
#             res['code'] = 1
#         res["pageCount"] = paginator.num_pages
#         res["recordCount"] = withdraw_list.count()
#     res["data"] = data
#     return JsonResponse(res)

def vip(request):
    return render(request, 'account/account_vip.html')

from django.db.models import Q

@csrf_exempt
@login_required
def project_manage(request):
    if request.method == "POST":
        user = request.user
        res={'code':0,}
        projects = Project.objects.filter(state__in=['10','20']).filter(Q(is_official=True) | Q(user__id=user.id))
        subprojects = SubscribeShip.objects.filter(user=user).values('project_id', 'price', 'is_recommend')
        subdic = {}
        for pro in subprojects:
            subdic[pro['project_id']] = pro
        page = request.GET.get("page", None)
        size = request.GET.get("size", 20)
        try:
            size = int(size)
        except ValueError:
            size = 20
        if not page or size <= 0:
            raise Http404
        item_list = projects
        paginator = Paginator(item_list, size)
        try:
            contacts = paginator.page(page)
        except PageNotAnInteger:
        # If page is not an integer, deliver first page.
            contacts = paginator.page(1)
        except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
            contacts = paginator.page(paginator.num_pages)
        data = []
        for con in contacts:
            is_on = con.id in subdic.keys()
            is_recom = False if not is_on else subdic[con.id]['is_recommend']
            price = '' if not is_on else subdic[con.id]['price']
            i = {"titile":con.title,
                 "soure":u"官方项目" if con.is_official else u"自建项目",
                 "state":con.get_state_display(),
                 "price":price,
                 "is_on":is_on, #是否主页呈现
                 "is_recom":is_recom,#是否在推荐位
                 }
            data.append(i)
        if data:
            res['code'] = 1
        res["pageCount"] = paginator.num_pages
        res["recordCount"] = item_list.count()
        res["data"] = data
        return JsonResponse(res)
    else:
        template = 'account/m_account_myproject.html' if request.mobile else 'account/account_myproject.html' 
        return render(request, template)

# 
# @csrf_exempt
# @login_required_ajax
# def project_create(request):
#     ret = {}
#     user = request.user
#     title = request.POST.get("title", None)
#     strategy = request.POST.get("strategy", None)
#     introduction = request.POST.get("introduction", None)
#     price = request.POST.get("price", None)
#     term = request.POST.get("term", None)
#     investrange = request.POST.get("investrange", None)
#     intrest = request.POST.get("intrest", None)
#     if not title or not strategy or not introduction:
#         ret['code'] = 1
#         ret['msg'] = u"参数缺失"
#     else:
#         with transaction.atomic():
#             points = random.randint(5,50)
#             print points
#             project = Project.objects.create(title=title, strategy=strategy, introduction=introduction,
#                     cprice=price, is_official=False, user=user, term=term, investrange=investrange,
#                     intrest=intrest, pic='', points=points)
#             SubscribeShip.objects.create(user=user, project=project, is_on=True)
#         ret['code'] = 0
#     return JsonResponse(ret)

@csrf_exempt
@login_required_ajax
def submit_screenshot(request):
    imgurl_list = []
    result = {}
    id = request.POST.get('id')
    investlog = InvestLog.objects.get(id=id)
    if len(request.FILES)>6:
        result = {'code':-2, 'msg':u"上传图片数量不能超过3张"}
        return JsonResponse(result)
    for key in request.FILES:
        block = request.FILES[key]
        if block.size > 100*1024:
            result = {'code':-1, 'msg':u"每张图片大小不能超过100k，请重新上传"}
            return JsonResponse(result)
    for key in request.FILES:
        block = request.FILES[key]
        imgurl = saveImgAndGenerateUrl(key, block, 'screenshot')
        imgurl_list.append(imgurl)
    invest_image = ';'.join(imgurl_list)
    investlog.invest_image = invest_image
    investlog.save(update_fields=['invest_image',])
    result['code'] = 0
    return JsonResponse(result)

@csrf_exempt
@login_required_ajax
def admin_investlog(request, id):
    log = InvestLog.objects.get(id=id)
    if not log.is_official:
        audit_state = request.POST['audit_state']
    
        if log.audit_state != '1':
            return JsonResponse({'code':1, 'msg':u"该项目已审核"})
        if audit_state == '0':
            log.settle_amount = request.POST['settle_amount']
            log.return_amount = request.POST['return_amount']
    
        else:
            log.audit_reason = request.POST['audit_reason']
        log.audit_state = audit_state
        log.audit_time = datetime.datetime.now()
    else:
        log.return_amount = request.POST['return_amount']
    log.save()
    return JsonResponse({'code':0})

def detail_investlog(request, id):
    investlog = get_object_or_404(InvestLog, id=id)
    kwargs = {'investlog':investlog, 'id':id}
    if investlog.is_official:
        template = 'account/m_detail_official_investlog.html'
    else:
        template = 'account/m_detail_personal_investlog.html'
    return render(request, template, kwargs)
    
# @csrf_exempt
# @login_required_ajax
# def project_add(request):
#     marks = Mark.objects.filter(user=request.user)
#     kwargs = {'marks':marks}
#     checked_marks = []
#     if not id is None:
#         id = int(id)
#         kwargs.update(id=id)
#         sub = get_object_or_404(SubscribeShip, project_id=id, user=request.user)
#         checked_marks = [ int(x.id) for x in sub.marks.all() ]
#     kwargs.update(checked_marks=checked_marks)
#     companies = Company.objects.all()
#     kwargs.update(companies=companies)
#     return render(request, 'account/project_add.html', kwargs)

@login_required
def quick_sumbit(request):
    user = request.user
    projects = Project.objects.filter(Q(user=user)|Q(is_official=True)).filter(state__in=['10', '20']).order_by('szm')
    dic = OrderedDict()
    for project in projects:
        id = project.id
        title = project.title
        if project.user == user and project.is_official==False:
            title += u"（自建项目）"
        logo = project.picture_url()
        szm = project.szm
        pinyin = project.pinyin
        necessary_fields = project.necessary_fields
        is_multisub_allowed = project.is_multisub_allowed
        key = szm[0:1]
        param = {}
        param.update(id=id, title=title, logo=logo, szm=szm, pinyin=pinyin, necessary_fields=necessary_fields,
                     is_multisub_allowed = is_multisub_allowed)
        prolist = dic.get(key, [])
        if not prolist:
            dic[key] = prolist
        prolist.append(param)
    template = 'account/m_quicksub.html'
    return render(request, template, {'projects':dic})
@login_required
def detail_project(request, id):
    project = Project.objects.get(id=id)
    kwargs = {'id':id, 'project':project}
    template = 'account/m_detail_project.html'
    return render(request, template , kwargs)

@csrf_exempt
@transaction.atomic
@login_required_ajax
def submitOrder(request):
    result = {}
    project_id = request.POST.get('project')
    invest_amount = request.POST.get('invest_amount')
    invest_term = request.POST.get('invest_term')
    invest_date = request.POST.get('invest_date')
    zhifubao = request.POST.get('zhifubao', '')
    qq_number = request.POST.get('qq_number', '')
    expect_amount = request.POST.get('expect_amount', '')
    invest_name = request.POST.get('invest_name', '')
    invest_mobile = request.POST.get('invest_mobile')
    remark = request.POST.get('remark', '')
    invest_amount = None if invest_amount=='' else invest_amount
    invest_term = None if invest_term=='' else invest_term
    invest_date = datetime.date.today() if invest_date=='' else invest_date
    submit_type = request.POST.get('submit_type', '1')
    project = Project.objects.get(id=project_id)
#     fields = re.split(r'[\s,]+', project.necessary_fields)
    if not ( project_id and invest_mobile ):
        result['code'] = 0
        result['msg'] = u"请提交投资手机号"
        return JsonResponse(result)
    if invest_date:
        invest_date = datetime.datetime.strptime(invest_date, "%Y-%m-%d")
    with cache.lock('project_submit_%s' % project.id, timeout=2):
        if not project.is_multisub_allowed or submit_type=='1':
            if project.company is None:
                queryset=InvestLog.objects.filter(invest_mobile=invest_mobile, project=project)
            else:
                queryset=InvestLog.objects.filter(invest_mobile=invest_mobile, project__company_id=project.company_id)
            if queryset.exclude(audit_state='2').exists():
                result['code'] = 1
                result['msg'] = u"该手机号（首投）已提交过，请勿重复提交"
                return JsonResponse(result)
    
        investlog=InvestLog.objects.create(user=request.user,project_id=project_id, invest_mobile=invest_mobile, invest_date=invest_date,
                                 invest_name=invest_name, remark=remark, qq_number=qq_number, expect_amount=expect_amount,
                                 zhifubao=zhifubao, invest_amount=invest_amount, submit_type=submit_type,
                                  invest_term=invest_term, is_official=project.is_official, category=project.category,
                                  submit_way='4', audit_state='1')
    #活动插入
#     on_submit(request, request.user, investlog)
    #活动插入结束

    result['code'] = 0
    return JsonResponse(result)

@csrf_exempt
@login_required_ajax
def reaudit(request):
    res = {}
    id = request.POST.get('id')
    reason = request.POST.get('reason')
    if not id or not reason:
        res['code'] = 1
        res['msg'] = u"参数不足"
        return JsonResponse(res)
    log = InvestLog.objects.get(user=request.user, id=id)
    log.reaudit_reason = u"用户申诉：" + reason
    log.audit_state = '3'
    log.save(update_fields=['audit_state', 'reaudit_reason'])
    res['code'] = 0
    return JsonResponse(res)






