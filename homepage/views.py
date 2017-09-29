from django.shortcuts import render
from wafuli.models import SubscribeShip, Notice
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def index(request):
    recoms = list(SubscribeShip.objects.filter(user=request.user, is_recommend=True, is_on=True)[0:10])
    if len(recoms)==0:
        recoms = list(SubscribeShip.objects.filter(user=request.user, is_on=True)[0:4])
    recom_list = []
    for r in recoms:
        p = r.project
        data = {
            'id':p.id,
            'title' : p.title,
            'intrest': r.intrest if r.intrest else p.intrest,
            'price': r.price if r.price else p.cprice,
            'term': p.term,
            'range': p.investrange,
            'pic': p.picture_url(),
            'investrange': p.investrange,
            'strategy': p.strategy,
            'state':p.state,
        }
        recom_list.append(data)
    notice_list = Notice.objects.filter(user=request.user)
    return render(request, 'my_homepage.html',{'recom_list':recom_list, 'notice_list':notice_list})

@login_required
def m_index(request):
    recoms = list(SubscribeShip.objects.filter(user=request.user, is_recommend=True, is_on=True)[0:10])
    if len(recoms)==0:
        recoms = list(SubscribeShip.objects.filter(user=request.user, is_on=True)[0:4])
    recom_list = []
    for r in recoms:
        p = r.project
        data = {
            'id':p.id,
            'title' : p.title,
            'intrest': r.intrest if r.intrest else p.intrest,
            'price': r.price if r.price else p.cprice,
            'term': p.term,
            'range': p.investrange,
            'pic': p.picture_url(),
            'investrange': p.investrange,
            'strategy': p.strategy,
            'state':p.state,
        }
        recom_list.append(data)
    notice_list = Notice.objects.filter(user=request.user)
    return render(request, 'm_homepage.html',{'recom_list':recom_list, 'notice_list':notice_list})
