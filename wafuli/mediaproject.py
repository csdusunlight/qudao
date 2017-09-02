#coding:utf-8
'''
Created on 2017年8月22日

@author: lvch
'''
from django.shortcuts import render
from wafuli.models import MediaProject, UserEvent
import logging
from django.http.response import Http404, JsonResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from wafuli.tools import saveImgAndGenerateUrl
from django.views.decorators.csrf import csrf_exempt
logger = logging.getLogger('wafuli')

# @login_required
@csrf_exempt
def media_submit(request):
    if request.method == 'POST':
        if not request.user.is_authenticated():
            result = {'code':-1,}
            return JsonResponse(result)
        news_id = request.POST.get('id', None)
        telnum = request.POST.get('telnum', '').strip()
        remark = request.POST.get('remark', '')
        amount = request.POST.get('amount', '')
        term = request.POST.get('term', '')
        invest_time = request.POST.get('date', '')
        if not (news_id and telnum and amount and term and invest_time):
            raise Http404
        amount = float(amount)
        news = MediaProject.objects.get(pk=news_id)
        code = None
        msg = ''
        userlog = None
        try:
            if not news.is_multisub_allowed and news.user_event.filter(invest_account=telnum).exclude(audit_state='2').exists():
                raise ValueError('This invest_account is repective in project:' + str(news.id))
            else:
                userlog = UserEvent.objects.create(user=request.user, event_type='9', invest_account=telnum,
                                 invest_image='', content_object=news, audit_state='1',remark=remark,
                                 invest_amount=amount, invest_term=term,invest_time=invest_time)
                code = 1
                msg = u'提交成功，请通过用户中心查询！'
        except Exception, e:
            logger.info(e)
            result = {'code':2, 'msg':u"该注册手机号已被提交过，请不要重复提交！"}
            return JsonResponse(result)
        else:
            if request.FILES:
                imgurl_list = []
                if len(request.FILES)>6:
                    result = {'code':-2, 'msg':u"上传图片数量不能超过6张"}
                    userlog.delete()
                    return JsonResponse(result)
                for key in request.FILES:
                    block = request.FILES[key]
                    if block.size > 100*1024:
                        result = {'code':-1, 'msg':u"每张图片大小不能超过100k，请重新上传"}
                        userlog.delete()
                        return JsonResponse(result)
                for key in request.FILES:
                    block = request.FILES[key]
                    imgurl = saveImgAndGenerateUrl(key, block)
                    imgurl_list.append(imgurl)
                invest_image = ';'.join(imgurl_list)
                userlog.invest_image = invest_image
                userlog.save(update_fields=['invest_image'])
        result = {'code':code, 'msg':msg}
        return JsonResponse(result)
    else:
        projects = MediaProject.objects.filter(state='1')
        return render(request, 'media-submit.html', {'projects':projects,})

