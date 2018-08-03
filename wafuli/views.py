# #coding:utf-8
from django.shortcuts import render

from wafuli_admin.models import GlobalStatis
from wafuli.models import MAdvert_PC, Project, Company, InvestLog
import logging
from django.http.response import Http404
from django.contrib.auth.decorators import login_required
from account.models import ApplyLog
logger = logging.getLogger('wafuli')

def index(request):
    data = {
        'invest_total':0,#引入资金
        'invite_total':0,#渠道引入用户数
        'with_total':0,#提现总额
        'user_total':0,#累计加入渠道数
    }
    global_data = GlobalStatis.objects.first()
    if global_data:
        data['invest_total']=global_data.invest_total
        data['invite_total']=global_data.invite_total
        data['with_total']=global_data.with_total
        data['user_total']=global_data.user_total

    #banner
    ad_list = MAdvert_PC.objects.filter(location='00', is_hidden=False)[0:6]
    data.update(ad_list=ad_list)

    #今日推荐项目
    recom_projects = Project.objects.filter(state='10', is_official=True, is_addedto_repo=True)[0:3]
    data.update(recom_projects=recom_projects)

    #合作平台
    platforms = Company.objects.order_by("-priority")[0:18]
    data.update(platforms=platforms)
    template = 'm_index.html' if request.mobile else 'index.html'
    return render(request, template, data)

def project_all(request):
    hot_platforms = Company.objects.order_by('-view_count')[0:6]
    print hot_platforms
    if request.user.is_authenticated():
        template = 'm_project_repo.html' if request.mobile else 'project_repo.html'
    else:
        template = 'm_project_repo_nologin.html' if request.mobile else 'project_repo.html'         #llc
    return render(request, template, {'hot_platforms':hot_platforms})

def project_all_scroll(request):        #jzy
    hot_platforms = Company.objects.order_by('-view_count')[0:6]
    print hot_platforms
    template = 'project_repo_scroll.html'
    return render(request, template, {'hot_platforms':hot_platforms})
   
def user_guide(request):
    return render(request, 'user_guide.html',  )
def activity_rank(request):
    return render(request, 'activity_rank.html',  )
@login_required
def display_screenshot(request):
    id = request.GET.get('id', None)
    if not id:
        raise Http404
    log = InvestLog.objects.get(id=id)
    if log.user.id != request.user.id and not request.user.is_staff:
        raise Http404
    url_list = log.invest_image.split(';')
    img_list = []
    for url in url_list:
        name = url.split('/')[-1]
        img_list.append({'name':name,'url':url})
    return render(request, 'screenshot.html', {'img_list':img_list})

@login_required
def display_qualification(request):
    id = request.GET.get('id', None)
    if not id:
        raise Http404
    log = ApplyLog.objects.get(id=id)
    if not request.user.is_staff:
        raise Http404
    url_list = log.qualification.split(';')
    img_list = []
    for url in url_list:
        name = url.split('/')[-1]
        img_list.append({'name':name,'url':url})
    return render(request, 'screenshot.html', {'img_list':img_list})

def cooperate(request):
    template = 'm_cooperation.html' if request.mobile else 'cooperation.html'
    return render(request, template)

def intro_fanshu_home(request):     #jzy
    template = 'intro_fanshu_home.html'
    return render(request, template)

def intro_settle_tool(request):     #jzy
    template = 'intro_settle_tool.html'
    return render(request, template)

def intro_fanshu_doc(request):     #jzy
    template = 'intro_fanshu_doc.html'
    return render(request, template)

def intro_merchant(request):     #jzy
    template = 'intro_merchant.html'
    return render(request, template)

def intro_about_us(request):     #jzy
    template = 'intro_about_us.html'
    return render(request, template)
