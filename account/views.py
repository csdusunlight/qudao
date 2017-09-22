#coding:utf-8
from django.shortcuts import render, redirect
from django.http.response import Http404
from .models import MyUser, Userlogin,MobileCode
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
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
from django.contrib.contenttypes.models import ContentType
from account.models import UserSignIn, BankCard, ApplyLog
from datetime import date, timedelta, datetime
import time as ttime
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Sum, Count
from transaction import charge_money
from account.tools import send_mail, get_client_ip
from django.db import connection, transaction
from wafuli.data import BANK
from wafuli.models import TransList, WithdrawLog, Project, SubscribeShip,\
    InvestLog
from public.tools import login_required_ajax
from wafuli.tools import saveImgAndGenerateUrl

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
            auth_login(request, user)
            # anything you can add here
#             user.last_login_time = user.this_login_time
#             user.this_login_time = datetime.now()
            Userlogin.objects.create(user=user,)
#             user.save(update_fields=["last_login_time", "this_login_time"])
            return HttpResponseRedirect(redirect_to)
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
        profile = request.POST.get('profile', '')
        if not (telcode and mobile and password and qq_number):
            result['code'] = '3'
            result['msg'] = u'传入参数不足！'
            return JsonResponse(result)
        if ApplyLog.objects.filter(mobile=mobile).exists():
            result['code'] = '1'
            result['msg'] = u'该手机号码已被注册，请直接登录！'
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

        try:
            username = 'v' + str(mobile)
            apply = ApplyLog(mobile=mobile, username=username, password=password,
                            qq_name=qq_name, qq_number=qq_number, profile=profile, audit_state='1')
            apply.save()
            logger.info('Creating ApplyLog:' + mobile + ' succeed!')
        except Exception,e:
            logger.error(e)
            result['code'] = '4'
            result['msg'] = u'创建申请失败！'
            return JsonResponse(result)
        imgurl_list = []
        if len(request.FILES)>6:
            result = {'code':-2, 'msg':u"上传图片数量不能超过6张"}
            apply.delete()
            return JsonResponse(result)
        for key in request.FILES:
            block = request.FILES[key]
            if block.size > 100*1024:
                result = {'code':-1, 'msg':u"每张图片大小不能超过100k，请重新上传"}
                apply.delete()
                return JsonResponse(result)
        for key in request.FILES:
            block = request.FILES[key]
            imgurl = saveImgAndGenerateUrl(key, block, 'qualification')
            imgurl_list.append(imgurl)
        invest_image = ';'.join(imgurl_list)
        apply.qualification = invest_image
        apply.save(update_fields=['qualification',])
        result['code'] = 0
        return JsonResponse(result)
    else:
        mobile = request.GET.get('mobile','')
        icode = request.GET.get('icode','')
        hashkey = CaptchaStore.generate_key()
        codimg_url = captcha_image_url(hashkey)
        icode = request.GET.get('icode','')
        context = {
            'hashkey':hashkey,
            'codimg_url':codimg_url,
            'icode':icode,
            'mobile':mobile,
        }
        return render(request,'registration/register.html', context)


def verifymobile(request):
    mobilev = request.GET.get('mobile', None)
    users = None
    code = '0' # is used
    if mobilev:
        users = ApplyLog.objects.filter(mobile=mobilev)
        if not users.exists():
            code = '1'
    result = {'code':code,}
    return JsonResponse(result)
def verifyusername(request):
    namev = request.GET.get('username', None)
    users = None
    code = '0' # is used
    if namev:
        users = ApplyLog.objects.filter(username=namev)
        if not users.exists():
            code = '1'
    result = {'code':code,}
    return JsonResponse(result)
def verifyqq(request):
    qqv = request.GET.get('qq_number', None)
    users = None
    code = '0' # is used
    if qqv:
        users = ApplyLog.objects.filter(qq_number=qqv)
        if not users.exists():
            code = '1'
    result = {'code':code,}
    return JsonResponse(result)
def verifyinviter(request):
    invite_code = request.GET.get('invite', None)
    code = '0' # not exist
    if invite_code:
        users = MyUser.objects.filter(invite_code=invite_code)
        if users.exists():
            code = '1'
    result = {'code':code,}
    return JsonResponse(result)
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
    if not request.is_ajax():
        raise Http404
    action = request.GET.get('action', None)
    result = {'code':'0', 'message':'hi!'}
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
            result['message'] = u'该手机号码已被占用！'
            result.update(generateCap())
            return JsonResponse(result)
    elif action=='forgot_passwd':
        hashkey = request.GET.get('hashkey', None)
        response = request.GET.get('response', None)
        if not (phone and hashkey and response):
            raise Http404
        ret = imageV(hashkey, response)
        if ret != 0:
            result['message'] = u'图形验证码输入错误！'
            return JsonResponse(result)
    stamp = str(phone)
    lasttime = request.session.get(stamp, None)
    now = int(ttime.time())
    if lasttime:
        dif = now - int(lasttime)
        if dif < 60:
            result['message'] = u'请不要频繁提交！'
            result.update(generateCap())
            return JsonResponse(result)
    today = date.today()
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
        result['code'] = '1'
        MobileCode.objects.create(mobile=phone,rand_code=ret,remote_ip=remote_ip)
        request.session[stamp] = now
    else:
        logger.error('Sending Varifing code to ' + phone + ' is failed!!!')
        result['message'] = u"发送验证码失败！"
    return JsonResponse(result)

@login_required
def account(request):
    return render(request, 'account/account_index.html',)

@login_required
def account_setting(request):
    return render(request, 'account/account_setting.html',)

@login_required
def account_submit(request):
    plist = list(Project.objects.filter(state__in=['10','20'], is_official=True))    #jzy
    return render(request, 'account/account_submit.html', {'plist':plist})

@login_required
def account_audited(request):
    return render(request, 'account/account_audited.html',)




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
def bankcard(request):
    user = request.user
    card = user.user_bankcard.first()
    banks = BANK
    return render(request, 'account/account_bankcard.html', {"card":card, 'banks':banks})

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

def bind_bankcard(request):
    result={'code':-1, 'url':''}
    if not request.is_ajax():
        raise Http404
    user = request.user
    if not user.is_authenticated():
        result['code'] = 1
        result['url'] = reverse('login') + "?next=" + reverse('bind_bankcard')
        return JsonResponse(result)
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
        print 'bank' + bank
        if card_number and real_name and bank:
            user.user_bankcard.create(user=user, card_number=card_number, real_name=real_name,
                                       bank=bank, subbranch=subbranch)
        result['code'] = 0
    return JsonResponse(result)

@login_required
def money(request):
    return render(request, 'account/money.html', {})

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
        hashkey = CaptchaStore.generate_key()
        codimg_url = captcha_image_url(hashkey)

        user = request.user
        card = user.user_bankcard.first()
        return render(request,'account/withdraw.html',
                  {'hashkey':hashkey, 'codimg_url':codimg_url, "card":card})
    elif request.method == 'POST':
        user = request.user
        result = {'code':-1, 'res_msg':''}
        withdraw_amount = request.POST.get("amount", None)
        varicode = request.POST.get('varicode', None)
        hashkey = request.POST.get('hashkey', None)
        if not (varicode and withdraw_amount and hashkey):
            result['code'] = 3
            result['res_msg'] = u'传入参数不足！'
            return JsonResponse(result)
        try:
            withdraw_amount = int(withdraw_amount)
        except ValueError:
            result['code'] = -1
            result['res_msg'] = u'参数不合法！'
            return JsonResponse(result)
        if withdraw_amount < 1000 or withdraw_amount > user.balance:
            result['code'] = -1
            result['res_msg'] = u'提现金额错误！'
            return JsonResponse(result)
        # if not user.zhifubao or not user.zhifubao_name:
        #     result['code'] = -1
        #     result['res_msg'] = u'请先绑定支付宝！'
        #     return JsonResponse(result)
        card = user.user_bankcard.first()
        if not card:
            result['code'] = -1
            result['res_msg'] = u'请先绑定银行卡！'
            return JsonResponse(result)

        ret = imageV(hashkey, varicode)
        if ret != 0:
            result['code'] = 2
            result['res_msg'] = u'图形验证码输入错误！'
            result.update(generateCap())
        else:
            try:
                with transaction.atomic():
                    translist = charge_money(user, '1', withdraw_amount, u'提现')
                    event = WithdrawLog.objects.create(user=user, amount=withdraw_amount, audit_state='1')
                    result['code'] = 0
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
        print subprojects
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
        return render(request, 'account/account_myproject.html')


@csrf_exempt
@login_required_ajax
def project_create(request):
    ret = {}
    user = request.user
    title = request.POST.get("title", None)
    strategy = request.POST.get("strategy", None)
    introduction = request.POST.get("introduction", None)
    price = request.POST.get("price", None)
    term = request.POST.get("term", None)
    investrange = request.POST.get("investrange", None)
    intrest = request.POST.get("intrest", None)
    if not title or not strategy or not introduction:
        ret['code'] = 1
        ret['msg'] = u"参数缺失"
    else:
        with transaction.atomic():
            project = Project.objects.create(title=title, strategy=strategy, introduction=introduction,
                    cprice=price, is_official=False, user=user, term=term, investrange=investrange,
                    intrest=intrest)
            SubscribeShip.objects.create(user=user, project=project, is_on=True)
        ret['code'] = 0
    return JsonResponse(ret)

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