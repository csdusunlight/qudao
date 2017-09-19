from django.shortcuts import render
from wafuli.models import SubscribeShip, Notice

# Create your views here.

def index(request):
    recoms = SubscribeShip.objects.filter(user=request.user, is_recommend=True)[0:10]
    recom_list = []
    for r in recoms:
        p = r.project
        data = {
            'id':p.id,
            'title' : p.title,
            'intrest': p.intrest,
            'price': p.cprice if not r.price else r.price,
            'term': p.term,
            'range': p.investrange,
            'pic': p.pic.url,
        }
        recom_list.append(data)
    notice_list = Notice.objects.filter(user=request.user)
    return render(request, 'my_homepage.html',{'recom_list':recom_list, 'notice_list':notice_list})
