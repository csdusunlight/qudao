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
from account.models import UserSignIn, EmailActCode, BankCard
from datetime import date, timedelta, datetime
import time as ttime
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from wafuli.models import (UserEvent, Finance, Task, ExchangeRecord,
    ScoreTranlist, TransList, Coupon, Message, MediaProject)
from django.db.models import Sum, Count
from .transaction import charge_money, charge_score
from account.tools import send_mail, get_client_ip
from django.db import connection
from wafuli.data import BANK
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
            user.last_login_time = user.this_login_time
            user.this_login_time = datetime.now()
            Userlogin.objects.create(user=user,)
            user.save(update_fields=["last_login_time", "this_login_time"])
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
def register(request):
    if request.method == 'POST':
        if not request.is_ajax():
            raise Http404
        result = {}
        telcode = request.POST.get('code', None)
        mobile = request.POST.get('mobile', None)
        password = request.POST.get('password', None)
        invite_code = request.POST.get('invite', None)
        if not (telcode and mobile and password):
            result['code'] = '3'
            result['msg'] = u'传入参数不足！'
            return JsonResponse(result)
        if MyUser.objects.filter(mobile=mobile).exists():
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
        inviter = None
        if invite_code:
            try:
                inviter = MyUser.objects.get(invite_code=invite_code)
            except MyUser.DoesNotExist:
                result['code'] = '2'
                result['msg'] = u'该邀请码不存在，请检查'
                return JsonResponse(result)
        try:
            username = 'w' + str(mobile)
            user = MyUser(mobile=mobile, username=username, inviter=inviter)
            user.set_password(password)
            user.save()
            logger.info('Creating User:' + mobile + ' succeed!')
            # 注册奖励2元
            reg_award = 200
            trans = charge_money(user, '0', reg_award, u"注册奖励")
            if trans:
                logger.debug('Registering Award money is successfully payed!')
            else:
                logger.debug('Registering Award money is failed to pay!!!')
        except Exception,e:
            logger.error(e)
            result['code'] = '4'
            result['msg'] = u'创建用户失败！'
        else:
            result['code'] = '0'
            # 邀请人奖励10积分
            if inviter:
                invite_award_scores = 10
                inviter.invite_scores += invite_award_scores
                translist = charge_score(inviter, '0', invite_award_scores, u"邀请奖励")
                if translist:
                    logger.debug('Inviting Award scores is successfully payed!')
                    inviter.save(update_fields=['invite_scores'])
                else:
                    logger.debug('Inviting Award scores is failed to pay!!!')
            try:
                userl = authenticate(username=username, password=password)
                auth_login(request, userl)
                user.this_login_time = datetime.now()
                Userlogin.objects.create(user=userl,)
            except:
                pass
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
@login_required
def get_nums(request):
    coupon_num = Coupon.objects.filter(user=request.user, is_used=False).count()
    message_num = Message.objects.filter(user=request.user, is_read=False).count()
    result = {'coupon_num':coupon_num,'message_num':message_num,}
    return JsonResponse(result)
def verifyemail(request):
    emailv = request.GET.get('email', None)
    users = None
    code = '0' # is used
    if emailv:
        users = MyUser.objects.filter(email=emailv)
        if not users.exists():
            code = '1'

    result = {'code':code,}
    return JsonResponse(result)
def verifymobile(request):
    mobilev = request.GET.get('mobile', None)
    users = None
    code = '0' # is used
    if mobilev:
        users = MyUser.objects.filter(mobile=mobilev)
        if not users.exists():
            code = '1'
    result = {'code':code,}
    return JsonResponse(result)
def verifyusername(request):
    namev = request.GET.get('username', None)
    users = None
    code = '0' # is used
    if namev:
        users = MyUser.objects.filter(username=namev)
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
    task_type = ContentType.objects.get_for_model(Task)
    finance_type = ContentType.objects.get_for_model(Finance)
    task_list = UserEvent.objects.filter(user=request.user, content_type = task_type)[0:3]
    finance_list = UserEvent.objects.filter(user=request.user, content_type = finance_type)[0:3]
    recomm_list1 = Task.objects.order_by("-view_count")[0:4]
    recomm_list2 = Finance.objects.filter(level__in=['all','normal']).order_by("-view_count")[0:4]
    recomm_list = list(recomm_list1) + list(recomm_list2)
    recomm_list.sort(key=lambda x:x.view_count, reverse=True)
    signin_last = UserSignIn.objects.filter(user=request.user).first()
    isSigned = False
    signed_conse_days = 0
    if signin_last:
        if signin_last.date >= date.today() - timedelta(days=1):
            signed_conse_days = signin_last.signed_conse_days
            if signin_last.date == date.today():
                isSigned = True
    coupons = Coupon.objects.filter(user=request.user, is_used=False)
    coupon_not_used = 0
    for coupon in coupons:
        if not coupon.is_expired():
            coupon_not_used += 1
    coupon_to_expired = 0
    coupons = Coupon.objects.filter(user=request.user, is_used=False)
    for coupon in coupons:
        if coupon.is_to_expired():
            coupon_to_expired += 1
    return render(request, 'account/account_index.html',
                    {
                        'task_list':task_list, 'finance_list':finance_list,
                         'recomm_list':recomm_list[0:4], 'coupon_not_used':coupon_not_used,
                        'isSigned':isSigned, 'signed_conse_days':signed_conse_days,
                        'coupon_to_expired':coupon_to_expired,
                    }

                  )

def signin(request):

    if not request.is_ajax():
        raise Http404

    result={'code':-1, 'url':''}
    if not request.user.is_authenticated():
        result['code'] = -1
        result['url'] = reverse('login') + "?next=" + reverse('account_index')
    else:
        signin_last = UserSignIn.objects.filter(user=request.user).first()
        if signin_last and signin_last.date == date.today():
            result['code'] = 1
        else:
            signed_conse_days = 1
            if signin_last and signin_last.date == date.today() - timedelta(days=1):
                signed_conse_days += signin_last.signed_conse_days
            UserSignIn.objects.create(user=request.user, date=date.today(), signed_conse_days=signed_conse_days)
            charge_score(request.user, '0', 5, u"签到奖励")
            if signed_conse_days%7 == 0:
                charge_score(request.user, '0', 20, u"连续签到7天奖励")
            result['code'] = 0
    return JsonResponse(result)

@login_required
def welfare(request):
    tcount = Task.objects.filter(state='1').count()
    fcount = Finance.objects.filter(state='1').count()
    ttype = ContentType.objects.get_for_model(Task)
    ftype = ContentType.objects.get_for_model(Finance)
    tcount_u = UserEvent.objects.filter(user=request.user.id, content_type = ttype.id).count()
    fcount_u = UserEvent.objects.filter(user=request.user.id, content_type = ftype.id).count()
    tsum = UserEvent.objects.filter(time__gte=date.today(), content_type = ttype.id).count()
    fsum = UserEvent.objects.filter(time__gte=date.today(), content_type = ftype.id).count()
    statis = {'tcount':tcount,'fcount':fcount,'tcount_u':tcount_u,'fcount_u':fcount_u,'tsum':tsum,'fsum':fsum}
    return render(request, 'account/welfare.html', {'statis':statis})


def get_user_wel_page(request):
    if not request.is_ajax():
        raise Http404
    res={'code':0,}
    if not request.user.is_authenticated():
        res['code'] = -1
        res['url'] = reverse('login') + "?next=" + reverse('account_welfare')
        return JsonResponse(res)
    tpage = request.GET.get("tpage", None)
    fpage = request.GET.get("fpage", None)
    mpage = request.GET.get("mpage", None)
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
    if not tpage and not fpage and not mpage or size <= 0 or filter < 0 or filter > 3:
        raise Http404
    item_list = []
    if tpage:
        page = tpage
        etype = ContentType.objects.get_for_model(Task)
    elif fpage:
        page = fpage
        etype = ContentType.objects.get_for_model(Finance)
    elif mpage:
        page = mpage
        etype = ContentType.objects.get_for_model(MediaProject)
    item_list = UserEvent.objects.filter(user=request.user, content_type = etype)
    if filter == 1:
        item_list = item_list.filter(audit_state='0')
    elif filter == 2:
        item_list = item_list.filter(audit_state='1')
    elif filter == 3:
        item_list = item_list.filter(audit_state='2')
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
        reason = con.remark
        if filter == 3:
            log = con.audited_logs.first()
            if log:
                reason = log.reason
        i = {"title":con.content_object.title,
             "username":con.invest_account,
             "time":con.time.strftime("%Y-%m-%d %H:%M:%S"),
             "state":con.get_audit_state_display(),
             "reason":reason,
             "id":con.id,
             "amount":con.invest_amount,
             "term":con.invest_term,
             }
        data.append(i)
    if data:
        res['code'] = 1
    res["pageCount"] = paginator.num_pages
    res["recordCount"] = item_list.count()
    res["data"] = data
    return JsonResponse(res)

def get_channel_result_page(request):
    if not request.is_ajax():
        raise Http404
    res={'code':0,}
    if not request.user.is_authenticated():
        res['code'] = -1
        res['url'] = reverse('login') + "?next=" + reverse('account_channel')
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
    etype = ContentType.objects.get_for_model(Finance)
    item_list = UserEvent.objects.filter(user=request.user, content_type = etype)
    if filter == 1:
        item_list = item_list.filter(audit_state='0')
    elif filter == 2:
        item_list = item_list.filter(audit_state='1')
    elif filter == 3:
        item_list = item_list.filter(audit_state='2')
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
        reason = ''
        if con.audit_state == '2':
            log = con.audited_logs.first()
            if log:
                reason = log.reason
        return_amount = ''
        if con.audit_state == '0':
            trans = con.translist.first()
            if trans:
                return_amount = trans.transAmount
        i = {"project":con.content_object.title,
             "mobile":con.invest_account,
             "invest_time":con.invest_time.strftime("%Y-%m-%d"),
             "audit_result":con.get_audit_state_display(),
             "refuse_reason": reason,
             "id":con.id,
             'remark':con.remark,
             'invest_term':con.invest_term,
             'invest_amount':con.invest_amount,
             'return_amount':return_amount,
             }
        data.append(i)
    if data:
        res['code'] = 1
    res["pageCount"] = paginator.num_pages
    res["recordCount"] = item_list.count()
    res["data"] = data
    return JsonResponse(res)

@login_required
def score(request):
    return render(request, 'account/score.html', {})

def get_user_score_page(request):
    res={'code':0,}
    if not request.user.is_authenticated():
        res['code'] = -1
        res['url'] = reverse('login') + "?next=" + reverse('account_score')
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

    item_list = ScoreTranlist.objects.filter(user=request.user)
    if filter == 0:
        item_list = item_list.filter(transType='0')
    elif filter == 1:
        item_list = item_list.filter(transType='1').select_related('user_event')
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
        i = {"item":con.reason,
             "amount":con.transAmount,
             "time":con.time.strftime("%Y-%m-%d %H:%M:%S"),
             "remark":con.remark,
             "id":con.pk,
             }
        if filter == 1:
            event = con.user_event
            i["state"]=event.get_audit_state_display() if event.event_type!='7' else "无"
        data.append(i)
    if data:
        res['code'] = 1
    res["pageCount"] = paginator.num_pages
    res["recordCount"] = item_list.count()
    res["data"] = data
    return JsonResponse(res)
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
def active_email(request):
    result={'code':-1, 'url':'asd'}
    if request.is_ajax():
        user = request.user
        if not user.is_authenticated():
            result['code'] = 1
            result['url'] = reverse('login') + "?next=" + reverse('active_email')
            return JsonResponse(result)
        code = send_mail(user.email, user.pk)
        if code:
            EmailActCode.objects.update_or_create(email=user.email, defaults={'rand_code':code})
            result['code'] = 0
        else:
            result['code'] = 2
        return JsonResponse(result)
    elif request.method == 'GET':
        code = request.GET.get("code", '')
        try:
            obj = EmailActCode.objects.get(rand_code=code)
            user = MyUser.objects.get(email=obj.email)
            user.is_email_authenticated = True
            user.save(update_fields=["is_email_authenticated"])
            return redirect('account_security')
        except Exception, e:
            logger.error(str(e))
            raise Http404
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
            translist = charge_money(user, '1', withdraw_amount, u'提现')
            if translist:
                event = UserEvent.objects.create(user=user, event_type='2', invest_account=card.card_number,
                            invest_amount=withdraw_amount, audit_state='1')
                translist.user_event = event
                translist.save(update_fields=['user_event'])
                result['code'] = 0
            else:
                result['code'] = -2
                result['res_msg'] = u'提现失败！'
        return JsonResponse(result)


@login_required
def coupon(request):
    user = request.user
    coupons = user.user_coupons.filter(is_used=False)
    dict = {
        'cash_num' : coupons.filter(project__ctype='0').count(),
        'interest_num' : coupons.filter(project__ctype='1').count(),
        'exc_num' : coupons.filter(project__ctype='2').count()
    }
    return render(request, 'account/account_coupon.html', {'dict':dict})
def get_user_coupon_page(request):
    res={'code':0,}
    if not request.user.is_authenticated():
        res['code'] = -1
        res['url'] = reverse('login') + "?next=" + reverse('account_coupon')
        return JsonResponse(res)
    page = request.GET.get("page", None)
    size = request.GET.get("size", 2)
    filter = request.GET.get("filter", '')
    try:
        size = int(size)
    except ValueError:
        size = 2
    if not page or not filter or size <= 0:
        raise Http404
    item_list = Coupon.objects.filter(user=request.user,project__ctype=str(filter),is_used=False).select_related('project')
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
        project = con.project
        i = {"title":project.title,
             "amount":project.amount,
             "introduction":project.introduction,
             "url":project.exp_code.url if project.isonMobile else "",
             "isonMobile": 1 if project.isonMobile else 0,
             'endtime':project.endtime,
             'id':con.id,
             "pro_id":project.id,
             'code':con.exchange_code
        }
        data.append(i)
    if data:
        res['code'] = 1
    res["pageCount"] = paginator.num_pages
    res["recordCount"] = item_list.count()
    res["data"] = data
    return JsonResponse(res)
def get_user_coupon_exchange_detail(request):
    res={'code':0,}
    if not request.user.is_authenticated():
        res['code'] = -1
        res['url'] = reverse('login') + "?next=" + reverse('account_coupon')
        return JsonResponse(res)
    page = request.GET.get("page", None)
    size = request.GET.get("size", 6)
    try:
        size = int(size)
    except ValueError:
        size = 6
    if not page or size <= 0:
        raise Http404
    item_list = UserEvent.objects.filter(user=request.user,event_type='4')
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
        coupon = con.content_object
        i = {"title":coupon.project.title,
             "amount":coupon.project.amount,
             "account":con.invest_account,
             "state":con.get_audit_state_display(),
             "state_int":con.audit_state,
             'remark':con.remark,
             'reason':'' if con.audit_state!='2' else con.audited_logs.first().reason,
             'time':con.time.strftime("%Y-%m-%d %H:%M:%S"),
             'type':coupon.project.get_ctype_display()
        }
        data.append(i)
    if data:
        res['code'] = 1
    res["pageCount"] = paginator.num_pages
    res["recordCount"] = item_list.count()
    res["data"] = data
    return JsonResponse(res)

def useCoupon(request):
    user = request.user
    res={'code':0,}
    if not user.is_authenticated():
        res['code'] = -1
        res['url'] = reverse('login') + "?next=" + reverse('account_coupon')
        return JsonResponse(res)
    coupon_id = request.POST.get('id', None)
    telnum = request.POST.get('telnum', None)
    invest_amount = request.POST.get('amount', None)
    invest_term = request.POST.get('term', None)
    remark = request.POST.get('remark', '')
    if coupon_id is None or telnum is None or invest_amount is None:
        logger.error("Coupon ID or telnum or amount is missing!!!")
        raise Http404
    invest_amount = int(float(invest_amount))
    coupon = Coupon.objects.get(pk=coupon_id)
    code=''
    msg=''
    if coupon.is_used:
        code = '2'
        msg = u'该优惠券已兑换，请查看兑换记录！'
    else:
        events = UserEvent.objects.filter(invest_account=telnum, event_type='4').exclude(audit_state='2')
        if events.exists():
            pro_list = []
            project = coupon.project
            for eve in events:
                cou = eve.content_object
                pro_list.append(cou.project)
            if project in pro_list:
                code = '2'
                msg = u'该账号已领取奖励，请不要重复提交！'
    if code!='2':
        UserEvent.objects.create(user=user, event_type='4', invest_account=telnum, invest_amount=invest_amount,
                     invest_term=invest_term, content_object=coupon, audit_state='1',remark=remark,)
        code = '1'
        msg = u'提交成功，请查看兑换记录！'
        coupon.is_used = True
        coupon.save(update_fields=['is_used'],)
    result = {'code':code, 'msg':msg}
    return JsonResponse(result)

@login_required
def message(request):
    if request.method == 'GET':
        return render(request,'account/account_message.html')
    elif request.method == 'POST':
        user = request.user
        id = request.POST.get('id', 0)
        try:
            msg = Message.objects.get(id=id)
            msg.is_read = True
            msg.save(update_fields=['is_read',])
        except:
            pass
        result = {}
        return JsonResponse(result)
def get_user_message_page(request):
    res={'code':0,}
    if not request.user.is_authenticated():
        res['code'] = -1
        res['url'] = reverse('login') + "?next=" + reverse('account_coupon')
        return JsonResponse(res)
    page = request.GET.get("page", None)
    size = request.GET.get("size", 5)
    try:
        size = int(size)
    except ValueError:
        size = 5
    if not page or size <= 0:
        raise Http404
    item_list = Message.objects.filter(user=request.user)
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
        i = {"title":con.title,
             'content':con.content,
             'id':con.id,
             'time':con.time.strftime("%Y-%m-%d"),
             'state':"on" if con.is_read else "",
        }
        data.append(i)
    if data:
        res['code'] = 1
    res["pageCount"] = paginator.num_pages
    res["recordCount"] = item_list.count()
    res["data"] = data
    return JsonResponse(res)

@login_required
def invite(request):
    inviter = request.user
    if request.method == 'GET':
        withdraw_thismonth = UserEvent.objects.filter(user__inviter=inviter, event_type='2',
                    audit_state='0',audit_time__year=ttime.localtime()[0],audit_time__month=ttime.localtime()[1]).\
                    aggregate(sumofwith=Sum('invest_amount'))
        acc_count = inviter.invitees.count()
        acc_with_count = UserEvent.objects.filter(user__inviter=inviter, event_type='2',
                    audit_state='0').values('user__mobile').distinct().order_by().count()
        this_month_award = float(withdraw_thismonth.get('sumofwith') or 0)*settings.AWARD_RATE
        this_month_award = int(this_month_award)
        statis = {
            'left_award':inviter.invite_account,
            'accu_invite_award':inviter.invite_income,
            'accu_invite_scores':inviter.invite_scores,
            'acc_count':acc_count,
            'acc_with_count':acc_with_count,
            'this_month_award':this_month_award,
        }
        return render(request,'account/account_invite.html', {'statis':statis})
    elif request.method == 'POST':
        result = {'code':-1, 'res_msg':''}
        left_award = inviter.invite_account
        if left_award == 0:
            result['res_msg'] = u'邀请奖励结余为0'
        else:
            translist = charge_money(inviter, '0', left_award, u'邀请奖励')
            if translist:
                inviter.invite_account = 0
                inviter.save(update_fields=['invite_account'])
                event = UserEvent.objects.create(user=inviter, event_type='5',
                            invest_amount=left_award, audit_state='1')
                translist.user_event = event
                translist.save(update_fields=['user_event'])
                result['code'] = 0
            else:
                result['code'] = -2
                result['res_msg'] = u'操作失败，请联系客服！'
        print result
        return JsonResponse(result)

def get_user_invite_page(request):
    if not request.is_ajax():
        raise Http404
    user = request.user
    res={'code':0,}
    if not user.is_authenticated():
        res['code'] = -1
        res['url'] = reverse('login') + "?next=" + reverse('account_invite')
        return JsonResponse(res)
    page = request.GET.get("page", None)
    size = request.GET.get("size", 6)
    filter = request.GET.get("filter",0)
    try:
        size = int(size)
    except ValueError:
        size = 6
    try:
        filter = int(filter)
    except ValueError:
        filter = 0
    if not page or size <= 0 or filter < 0 or filter > 2:
        raise Http404

    data = []
    if filter == 0:
        invitees = user.invitees.all()
        paginator = Paginator(invitees, size)
        try:
            contacts = paginator.page(page)
        except PageNotAnInteger:
        # If page is not an integer, deliver first page.
            contacts = paginator.page(1)
        except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
            contacts = paginator.page(paginator.num_pages)
        for con in contacts:
            reg = UserEvent.objects.filter(user=con, event_type='2',audit_state='0').exists()
            mobile = con.mobile
            if len(mobile)==11:
                mobile = mobile[0:3] + '****' + mobile[7:]
            i = {
                 "mobile":mobile,
                 "time":con.date_joined.strftime("%Y-%m-%d %H:%M"),
                 "is_bind":u'是' if con.user_bankcard else u'否',
                 "is_with":u'是' if reg else u'否',
             }
            data.append(i)
        if data:
            res['code'] = 1
        res["pageCount"] = paginator.num_pages
        res["recordCount"] = invitees.count()
    elif filter == 1:
        events = UserEvent.objects.filter(user__inviter=user, event_type='2', audit_state='0')
        paginator = Paginator(events, size)
        try:
            contacts = paginator.page(page)
        except PageNotAnInteger:
        # If page is not an integer, deliver first page.
            contacts = paginator.page(1)
        except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
            contacts = paginator.page(paginator.num_pages)
        for con in contacts:
            take_award = float(con.invest_amount)*settings.AWARD_RATE
            take_award = int(take_award)
            i = {
                 "mobile":con.user.mobile,
                 "time":con.audit_time.strftime("%Y-%m-%d %H:%M"),
                 "amount":con.invest_amount,
                 "take":take_award,
             }
            data.append(i)
        if data:
            res['code'] = 1
        res["pageCount"] = paginator.num_pages
        res["recordCount"] = events.count()
    elif filter == 2:
        select = {'month': connection.ops.date_trunc_sql('month', 'time')}
        withdraw_list = UserEvent.objects.filter(user__inviter=user, event_type='2',
                audit_state='0',).extra(select=select)\
                .values('month').annotate(cou=Count('user',distinct=True),sumofwith=Sum('invest_amount')).order_by('-month',)
        paginator = Paginator(withdraw_list, size)

        try:
            contacts = paginator.page(page)
        except PageNotAnInteger:
        # If page is not an integer, deliver first page.
            contacts = paginator.page(1)
        except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
            contacts = paginator.page(paginator.num_pages)
        for con in contacts:
            take_award = float(con['sumofwith'] or 0)*settings.AWARD_RATE
            take_award = int(take_award)
            i = {
                 "month":str(con['month'])[0:7],
                 "amount":con['sumofwith'] or 0,
                 "cou":con['cou'],
                 "take":take_award,
                 "score":con['cou']*100,
             }
            data.append(i)
        if data:
            res['code'] = 1
        res["pageCount"] = paginator.num_pages
        res["recordCount"] = withdraw_list.count()
    res["data"] = data
    return JsonResponse(res)

def vip(request):
    return render(request, 'account/account_vip.html')

