# #coding:utf-8
# from django.shortcuts import render
#
# from django.http.response import Http404
# from wafuli.models import Welfare, Task, Finance, Commodity, Information, \
#     ExchangeRecord, Press, UserEvent, Advertisement, Activity, Company,\
#     CouponProject, Baoyou, Hongbao, UserTask, MAdvert_PC, Fuligou, CreditCard,\
#     Loan
# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# from django.core.urlresolvers import reverse
# from django.http import JsonResponse
# from account.transaction import charge_score
# from django.db.models import F,Q
# import logging
# from datetime import date, datetime
# from wafuli_admin.models import DayStatis, GlobalStatis, RecommendRank,\
#     UserStatis
# from account.models import MyUser, UserSignIn
# from django.contrib.contenttypes.models import ContentType
# from django.db import transaction
# from wafuli.public import update_view_count
# from .public import saveImgAndGenerateUrl
# from django.contrib.auth.decorators import login_required
# from rest_framework import generics
# from wafuli.serializers import HongbaoSerializer
# import django_filters
# from rest_framework.filters import OrderingFilter, SearchFilter
# from project_admin.Paginations import ProjectPageNumberPagination
# logger = logging.getLogger('wafuli')
# from .public import listing
# import re
#
from django.shortcuts import render
from wafuli_admin.models import GlobalStatis
from wafuli.models import MAdvert_PC, Project, Company, InvestLog
import logging
from django.http.response import Http404
from django.contrib.auth.decorators import login_required
from account.models import ApplyLog
logger = logging.getLogger('wafuli')
def index(request):
    logger.error(request.user.username)
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
    recom_projects = Project.objects.filter(state='10')[0:3]
    data.update(recom_projects=recom_projects)

    #合作平台
    platforms = Company.objects.order_by("-priority")
    data.update(platforms=platforms)
    return render(request, 'wfl-index.html', data)
def project_all(request):
    return render(request, 'finance_all.html',  )
#     ad_list = Advertisement.objects.filter(Q(location='0')|Q(location='1'),is_hidden=False)[0:8]
#     announce_list = Press.objects.filter(type='1')[0:5]
#     hongbao_list = Hongbao.objects.filter(is_display=True,state='1')[0:3]
#     baoyou_list = Baoyou.objects.filter(is_display=True,state='1')[0:3]
#     youhuiquan_list = CouponProject.objects.filter(is_display=True,state='1')[0:3]
#     for wel in youhuiquan_list:
#         wel.draw_count = wel.coupons.filter(user__isnull=False).count()
#         if wel.ctype == '2':
#             wel.left_count = wel.coupons.filter(user__isnull=True).count()
#         else:
#             wel.left_count = u"充足"
#     query_set = Finance.objects.filter(state__in=['1','2'], level__in=['all','normal']).order_by("state","-news_priority","-pub_date")
#     finance_list1 = query_set.filter(f_type='1')[0:3]
#     finance_list2 = query_set.filter(f_type='2')[0:3]
#     finance_list3 = query_set.filter(f_type='3')[0:3]
#     news_list = Activity.objects.filter(is_hidden=False)[0:2]
#     exchange_list = ExchangeRecord.objects.all()[0:10]
#     strategy_list = Press.objects.filter(type='2')[0:6]
#     info = Information.objects.filter(is_display=True).first()
#     context = {'ad_list':ad_list,
#                'hongbao_list': hongbao_list,
#                'baoyou_list': baoyou_list,
#                'youhuiquan_list': youhuiquan_list,
# #                'task_list': task_list,
#                'announce_list':announce_list,
#                'finance_list1': finance_list1,
#                'finance_list2': finance_list2,
#                'finance_list3': finance_list3,
#                'news_list': news_list,
#                'exchange_list': exchange_list,
#                'strategy_list': strategy_list,
#                'info': info,
#     }
#     task_list = list(Task.objects.filter(state__in=['1','2'],type='junior').order_by("state","-news_priority","-pub_date")[0:2])
#     if len(task_list)==2:
#         context.update(task1=task_list[0],task2=task_list[1])
#     task_list = list(Task.objects.filter(state__in=['1','2'],type='middle').order_by("state","-news_priority","-pub_date")[0:2])
#     if len(task_list)==2:
#         context.update(task3=task_list[0],task4=task_list[1])
#     task_list = list(Task.objects.filter(state__in=['1','2'],type='senior').order_by("state","-news_priority","-pub_date")[0:2])
#     if len(task_list)==2:
#         context.update(task5=task_list[0],task6=task_list[1])
#
#     try:
#         statis = DayStatis.objects.get(date=date.today())
#     except:
#         new_wel_num = 0
#     else:
#         new_wel_num = statis.new_wel_num
#     glo_statis = GlobalStatis.objects.first()
#     if glo_statis:
#         all_wel_num = glo_statis.all_wel_num
#         withdraw_total = int(glo_statis.award_total/100.0)
#
#     else:
#         withdraw_total = 0
#         all_wel_num = 0
#     context.update({'new_wel_num':new_wel_num, 'all_wel_num':all_wel_num, 'withdraw_total':withdraw_total})
#     return render(request, 'wfl-index.html', context)
# def wfl_index(request):
#     ad_list = MAdvert_PC.objects.filter(location='00', is_hidden=False)[0:6]
#     announce_list = Press.objects.filter(type='1')[0:2]
# #     hongbao_list = Hongbao.objects.filter(is_qualified=True,state='1').order_by("-startTime")[0:4]
#     fuligou_main = Fuligou.objects.filter(is_main=True)[0:4]
#     fuligou_side = Fuligou.objects.filter(is_main=False)[0:4]
#     task_list = Task.objects.filter(state='1').order_by("-news_priority","-pub_date")[0:4]
#     finance_list = Finance.objects.filter(state='1', level__in=['all','normal']).order_by("-news_priority","-pub_date")[0:3]
#     commodity_list = Commodity.objects.all()[0:6]
#     info = Information.objects.filter(is_display=True).first()
#     recom_list = MAdvert_PC.objects.filter(location='01',is_hidden=False)[0:4]
#     find = MAdvert_PC.objects.filter(location='02',is_hidden=False).first()
#     adv_middle = MAdvert_PC.objects.filter(location='03',is_hidden=False).first()
#     adv_bottom = MAdvert_PC.objects.filter(location='04',is_hidden=False).first()
#     credit_list = CreditCard.objects.all()[0:4]
#     loan_list = Loan.objects.all()[0:4]
#     week_statis = UserStatis.objects.order_by('-week_statis')[0:8]
#     month_statis = UserStatis.objects.order_by('-month_statis')[0:8]
#     context = {'ad_list':ad_list, #banner
# #                'hongbao_list': hongbao_list, #红包精选4个
#                'fuligou_main': fuligou_main, #福利购正文部分的4个
#                'fuligou_side': fuligou_side,#福利购边栏4个
#                'task_list': task_list, #任务福利4个
#                'announce_list':announce_list, #福利头条，第二屏，两个通知
#                'finance_list': finance_list, #理财福利，三个，前两个可以放到福利头条第三屏
#                'commodity_list': commodity_list,#边栏积分商品，6个
#                'recom_list': recom_list,#热门推荐，4个
#                'find': find,#发现，1个
#                'adv_middle':adv_middle,#首页中部横幅广告位
#                'adv_bottom':adv_bottom,#首页底部广告位
#                'credit_list': credit_list,#信用卡，4个
#                'loan_list': loan_list,#借点钱，4个
#                'week_statis':week_statis,#提现金额周排名前8
#                'month_statis':month_statis,#提现金额月排名前8
#     }
#
#
#     try:
#         statis = DayStatis.objects.get(date=date.today())
#     except:
#         new_wel_num = 0
#     else:
#         new_wel_num = statis.new_wel_num
#     glo_statis = GlobalStatis.objects.first()
#     if glo_statis:
#         all_wel_num = glo_statis.all_wel_num
#         withdraw_total = int(glo_statis.award_total/100.0)
#
#     else:
#         withdraw_total = 0#提现总额
#         all_wel_num = 0
#     context.update({'new_wel_num':new_wel_num, 'all_wel_num':all_wel_num, 'withdraw_total':withdraw_total})
#     if request.user.is_authenticated():
#         isSigned = False
#         try:
#             signin_last = UserSignIn.objects.get(user=request.user, date=date.today())
#         except:
#             isSigned = False
#         else:
#             isSigned = True
#         context.update(isSigned=isSigned)
#
#     return render(request, 'wfl-index.html', context)
# # def get_hongbao_by_type(request):
# #     htype = request.GET.get('type', None)
# #     order = request.GET.get('type', 0)
# #     order = int(order)
# #     if htype is None:
# #         hongbao_list = Hongbao.objects.filter(state='1', is_qualified=True)
# #     else:
# #         hongbao_list = Hongbao.objects.filter(htype=htype)
# #     if order == 0:
# #         hongbao_list = hongbao_list.order_by('-up')
# #     else:
# #         hongbao_list = hongbao_list.order_by("-startTime")
# #     ret = []
# #     for item in hongbao_list:
# #         ret.append({
# #             'subtitle':
# #         })
# #
# class HongbaoList(generics.ListCreateAPIView):
#     queryset = Hongbao.objects.all()
#     serializer_class = HongbaoSerializer
#     filter_backends = (SearchFilter, django_filters.rest_framework.DjangoFilterBackend, OrderingFilter)
#     filter_fields = ['state','htype','is_qualified']
#     ordering_fields = ('up','startTime')
#     search_fields = ('title', 'subtitle', 'provider', 'seo_description')
#     pagination_class = ProjectPageNumberPagination
#
# def hongbao(request, id):
#     if id is None:
#         ad_list = MAdvert_PC.objects.filter(location='10', is_hidden=False)[0:6]
#         ad_list2 = MAdvert_PC.objects.filter(location='11', is_hidden=False)[0:4]
#         fuligou_side = Fuligou.objects.filter(is_main=False)[0:5]
#         commodity_list = Commodity.objects.all()[0:5]
#         context = {
#             'ad_list':ad_list,
#             'ad_list2':ad_list2,
#             'fuligou_side':fuligou_side,
#             'commodity_list':commodity_list
#         }
#         return render(request, 'wfl-welfare.html', context)
#     else:
#         id = int(id)
#         news = Hongbao.objects.get(id=id)
#         other_hongbao_list = Hongbao.objects.filter(state='1').order_by('-up')[0:6]
#         like_hongbao_list = Hongbao.objects.filter(state='1',htype=news.htype).order_by('-startTime')[0:4]
#         next = Hongbao.objects.filter(id__gt=id).order_by('id').first()
#         prev = Hongbao.objects.filter(id__lt=id).order_by('-id').first()
#         context = {
#                    'news':news,
#                    'other_hongbao_list':other_hongbao_list,
#                    'like_hongbao_list':like_hongbao_list,
#                    'next':next,
#                    'prev':prev,
#         }
#         return render(request, 'wfl-welfare-detail.html', context)
# def updown_hongbao(request, id):
#     click = request.GET.get('click', 'up')
#     hongbao = Hongbao.objects.get(id=id)
#     if click == 'up':
#         hongbao.up = F('up') + 1
#         hongbao.save(update_fields=['up',])
#     elif click == 'down':
#         hongbao.down = F('down') + 1
#         hongbao.save(update_fields=['down',])
#     return JsonResponse({})
#
#
# def finance(request, id=None):
#     if id is None:
#         ad_list = Advertisement.objects.filter(Q(location='0')|Q(location='4'),is_hidden=False)[0:8]
#         strategy_list = Press.objects.filter(type='2')[0:10]
#         context = {'ad_list':ad_list,'strategy_list':strategy_list}
#         rank_users = MyUser.objects.order_by('-accu_income')[0:6]
#         for i in range(len(rank_users)):
#             key = 'rank'+str(i+1)
#             username = rank_users[i].username
#             if len(username) > 4:
#                 username = username[0:4] + '****'
#             else:
#                 username = username + '****'
#             income = rank_users[i].accu_income
#             context.update({key:{'username':username,'income':str(income)}})
#         return render(request, 'finance.html',context)
#     else:
#         id = int(id)
#         news = None
#         try:
#             news = Finance.objects.get(id=id)
#         except Finance.DoesNotExist:
#             raise Http404(u"该页面不存在")
#         update_view_count(news)
#         scheme = news.scheme
#         table = []
#         str_rows = scheme.split('|')
#         for str_row in str_rows:
#             row = str_row.split('#')
#             table.append(row);
#         other_wel_list = Finance.objects.filter(state='1', level__in=['normal','all']).order_by('-view_count')[0:10]
#         context = {
#                    'news':news,
#                    'type':'Finance',
#                    'other_wel_list':other_wel_list,
#                    'table':table,
#         }
#         return render(request, 'detail-finance.html', context)
#
# def task(request, id=None):
#     if id is None:
#         ad_list = Advertisement.objects.filter(Q(location='0')|Q(location='3'),is_hidden=False)[0:8]
#         strategy_list = Press.objects.filter(type='2')[0:10]
#         context = {'ad_list':ad_list,'strategy_list':strategy_list}
#         task_type = ContentType.objects.get_for_model(Task)
#         event_list = UserEvent.objects.filter(event_type='1',content_type = task_type.id)[0:6]
#         exps = []
#         for event in event_list:
#             username = event.user.username
#             task = event.content_object
#             if len(username) > 4:
#                 username = username[0:4] + '****'
#             else:
#                 username = username + '****'
#             exps.append({'username':username,'title':task.title})
#         context.update({'exps':exps})
#         defalut_filter = request.GET.get('type','')
#         if defalut_filter=='junior':
#             context.update(defalut_filter=1)
#         elif defalut_filter=='middle':
#             context.update(defalut_filter=2)
#         elif defalut_filter=='senior':
#             context.update(defalut_filter=3)
#         else:
#             context.update(defalut_filter=0)
#         return render(request, 'taskWelfare.html', context)
#     else:
#         id = int(id)
#         news = None
#         try:
#             news = Task.objects.get(id=id)
#         except Task.DoesNotExist:
#             raise Http404(u"该页面不存在")
#         update_view_count(news)
#         other_wel_list = Task.objects.filter(state='1').order_by('-view_count')[0:10]
#         context = {'news':news,'type':'Task','other_wel_list':other_wel_list}
#         if request.user.is_authenticated():
#             try:
#                 UserTask.objects.get(user=request.user,task=news)
#             except UserTask.DoesNotExist:
#                 context.update(accepted=0)
#             else:
#                 context.update(accepted=1)
#         else:
#             context.update(accepted=0)
#         return render(request, 'detail-task.html',context)
# def commodity(request, id):
#     id = int(id)
#     try:
#         com = Commodity.objects.get(id=id)
#     except Commodity.DoesNotExist:
#         raise Http404(u"该页面不存在")
#     return render(request, 'detail-commodity.html',{'com':com})
# def press(request, id):
#     id = int(id)
#     try:
#         press = Press.objects.get(id=id)
#     except Press.DoesNotExist:
#         raise Http404(u"该页面不存在")
#     return render(request, 'detail-press.html',{'press':press})
#
# def aboutus(request):
#     ad_list = Advertisement.objects.filter(Q(location='0')|Q(location='6'),is_hidden=False).first
#     return render(request, 'aboutus.html',{'ad_list':ad_list})
#
# # def experience_taskandfinance(request):
# #     if not request.is_ajax():
# #         logger.warning("Experience refused no-ajax request!!!")
# #         raise Http404
# #     code = '0'
# #     url = ''
# #     if not request.user.is_authenticated():
# #         url = reverse('login') + '?next=' + request.META['HTTP_REFERER']
# #         result = {'code':code, 'url':url}
# #         return JsonResponse(result)
# #     news_id = request.GET.get('id', None)
# #     news_type = request.GET.get('type', None)
# #     if not (news_id and news_type):
# #         logger.error("news_id or news_type is missing!!!")
# #         raise Http404
# #     news = None
# #     model = globals()[news_type]
# #     news = model.objects.get(pk=news_id)
# #     code = '1'
# #     if news.isonMobile:
# #         url = news.exp_code.url
# #     else:
# #         url = news.exp_url
# #     result = {'code':code, 'url':url}
# #     return JsonResponse(result)
# from decimal import Decimal
# def expsubmit_finance(request):
#     if not request.is_ajax():
#         logger.warning("Expsubmit refused no-ajax request!!!")
#         raise Http404
#     code = '0'
#     url = ''
#     if not request.user.is_authenticated():
#         url = reverse('login') + '?next=' + request.META['HTTP_REFERER']
#         result = {'code':-1, 'url':url}
#         return JsonResponse(result)
#     ret = {}
#     data = request.POST.get('data','')
#     if not data:
#         ret['code'] = 1
#         ret['msg'] = u'参数缺失'
#         return JsonResponse(ret)
#     table = data.split('$')
#     suc_num = 0
#     exist_num = 0   #jzy
#     exist_phone = ""   #jzy
#     for row in table:
#         temp = row.split('|')
#         news = Finance.objects.get(id=temp[0])
#         time = datetime.strptime(temp[1],'%Y-%m-%d')
#         telnum = temp[2]
#         amount = temp[3]
#         term = temp[4]
#         remark = temp[5]
#         try:
#             if not news.is_multisub_allowed and news.user_event.filter(invest_account=telnum).exclude(audit_state='2').exists():
#                 exist_num += 1   #jzy
#                 exist_phone = exist_phone + telnum + ", "   #jzy
#                 raise ValueError('This invest_account is repective in project:' + str(news.id))
#             else:
#                 UserEvent.objects.create(user=request.user, invest_time=time, event_type='1', invest_account=telnum, invest_term=term,
#                                  invest_amount=int(amount), content_object=news, audit_state='1',remark=remark,)
#                 suc_num += 1
#         except Exception, e:
#             logger.info(e)
#     result = {'code':0, 'suc_num':suc_num, 'exist_num':exist_num, 'exist_phone':exist_phone}   #jzy
#     return JsonResponse(result)
#
# def expsubmit_task(request):
#     if not request.is_ajax():
#         logger.warning("Expsubmit refused no-ajax request!!!")
#         raise Http404
#     if not request.user.is_authenticated():
#         url = reverse('login') + '?next=' + request.META['HTTP_REFERER']
#         result = {'code':0, 'url':url}
#         return JsonResponse(result)
#     news_id = request.POST.get('id', None)
#     telnum = request.POST.get('telnum', '').strip()
#     remark = request.POST.get('remark', '')
#     if not (news_id and telnum):
#         raise Http404
#     news = Task.objects.get(pk=news_id)
#     try:
#         record = UserTask.objects.get(user=request.user,task=news)
#     except UserTask.DoesNotExist:
#         result = {'code':3, 'msg':u"请先领取任务再提交！"}
#         return JsonResponse(result)
#     code = None
#     msg = ''
#     userlog = None
#     try:
#         with transaction.atomic():
#             if news.user_event.filter(invest_account=telnum).exclude(audit_state='2').exists():
#                 raise ValueError('This invest_account is repective in project:' + str(news.id))
#             else:
#                 userlog = UserEvent.objects.create(user=request.user, event_type='1', invest_account=telnum,
#                                  invest_image='', content_object=news, audit_state='1',remark=remark,)
#                 code = 1
#                 msg = u'提交成功，请通过用户中心查询！'
#     except Exception, e:
#         logger.info(e)
#         result = {'code':2, 'msg':u"该注册手机号已被提交过，请不要重复提交！"}
#         return JsonResponse(result)
#     else:
#         imgurl_list = []
#         if len(request.FILES)>6:
#             result = {'code':-2, 'msg':u"上传图片数量不能超过6张"}
#             userlog.delete()
#             return JsonResponse(result)
#         for key in request.FILES:
#             block = request.FILES[key]
#             if block.size > 100*1024:
#                 result = {'code':-1, 'msg':u"每张图片大小不能超过100k，请重新上传"}
#                 userlog.delete()
#                 return JsonResponse(result)
#         for key in request.FILES:
#             block = request.FILES[key]
#             imgurl = saveImgAndGenerateUrl(key, block)
#             imgurl_list.append(imgurl)
#         invest_image = ';'.join(imgurl_list)
#         userlog.invest_image = invest_image
#         userlog.save(update_fields=['invest_image'])
#         record.delete()
#     result = {'code':code, 'msg':msg}
#     return JsonResponse(result)
#
# def mall(request):
#     ad_list = Advertisement.objects.filter(Q(location='0')|Q(location='5'),is_hidden=False)[0:8]
#     help_list = Press.objects.filter(type='5')[0:10]
#     type = request.GET.get("type", "")
#     return render(request, 'mall.html', {'ad_list':ad_list,'type':type,'help_list':help_list})
# def get_commodity_page(request):
#     res={'code':0,}
#     page = request.GET.get("page", None)
#     size = request.GET.get("size", 16)
#     cat = request.GET.get("cat", None)
#     pro = request.GET.get("pro", None)
#     try:
#         size = int(size)
#     except ValueError:
#         size = 16
#     if not page or size <= 0:
#         raise Http404
#     item_list = Commodity.objects.all()
#     if cat:
#         item_list = item_list.filter(category=cat)
#     if pro:
#         item_list = item_list.filter(item=pro)
#     paginator = Paginator(item_list, size)
#     try:
#         contacts = paginator.page(page)
#     except PageNotAnInteger:
#     # If page is not an integer, deliver first page.
#         contacts = paginator.page(1)
#     except EmptyPage:
#     # If page is out of range (e.g. 9999), deliver last page of results.
#         contacts = paginator.page(paginator.num_pages)
#     data = []
#     for con in contacts:
#         i = {"name":con.name,
#              "price":con.price,
#              "url":con.url,
#              "pic":con.pic.url,
#              }
#         data.append(i)
#     if data:
#         res['code'] = 1
#     res["pageCount"] = paginator.num_pages
#     res["recordCount"] = item_list.count()
#     res["data"] = data
#     return JsonResponse(res)
#
# #查询订单详情
# def lookup_order(request):
#     if not request.is_ajax():
#         raise Http404
#     result={'code':-1, 'url':''}
#     if not request.user.is_authenticated():
#         result['code'] = -1
#         result['url'] = reverse('login') + "?next=" + reverse('account_score')
#         return JsonResponse(result)
#     id = request.GET.get("id", None)
#     if not id:
#         return Http404
#     try:
#         id = int(id)
#     except ValueError:
#         return Http404
#     try:
#         record = ExchangeRecord.objects.get(tranlist_id=id)
#     except ExchangeRecord.DoesNotExist:
#         result['code'] = 1
#     except Exception as e:
#         logger.error(e.reason)
#     else:
#         result['name'] = record.name
#         result['tel'] = record.tel
#         result['addr'] = record.addr
#         result['mes'] = record.message
#         result['code'] = 0
#     return JsonResponse(result)
#
# def submit_order(request):
#     if not request.is_ajax():
#         raise Http404
#     result={'code':-1, 'url':''}
#     if not request.user.is_authenticated():
#         result['code'] = -1
#         result['url'] = reverse('login') + "?next=" + reverse('account_score')
#         return JsonResponse(result)
#     name = request.GET.get("name", '')
#     tel = request.GET.get("tel", '')
#     addr = request.GET.get("addr", '')
#     remark= request.GET.get("remark", '')
#     good_id= request.GET.get("id", '')
#     if not (name and tel and addr and good_id):
#         return Http404
#     try:
#         good_id = int(good_id)
#     except ValueError:
#         return Http404
#     commodity = Commodity.objects.get(pk=good_id)
#     ret = charge_score(request.user, '1', commodity.price, commodity.name)
#     if ret is not None:
#         logger.debug('Exchanging scores is successfully reduced!')
#         exg_obj = ExchangeRecord.objects.create(tranlist=ret,commodity=commodity,
#                                       name=name,tel=tel,addr=addr,message=remark)
#         event = UserEvent.objects.create(user=request.user, event_type='3',invest_amount=commodity.price,
#                          audit_state='1',remark=remark, content_object=exg_obj)
#         ret.user_event = event
#         ret.save(update_fields=['user_event'])
#         result['code'] = 0
#     else:
#         logger.debug('Exchanging scores is failed to reduce!!!')
#         result['code'] = 1
#     return JsonResponse(result)
#
# def get_finance_page(request):
#     res={'code':0,}
#     page = request.GET.get("page", None)
#     size = request.GET.get("size", 5)
#     filter = request.GET.get("filter", 0)
#     state = request.GET.get("state", 0)
#     try:
#         size = int(size)
#     except ValueError:
#         size = 6
#     if not page or size <= 0:
#         raise Http404
#     item_list = Finance.objects.filter(level__in=['normal','all'])
#     filter = str(filter)
#     state = str(state)
#     if filter != '0':
#         item_list = item_list.filter(f_type=filter)
#     item_list = item_list.filter(state=state)
#     paginator = Paginator(item_list, size)
#     try:
#         contacts = paginator.page(page)
#     except PageNotAnInteger:
#     # If page is not an integer, deliver first page.
#         contacts = paginator.page(1)
#     except EmptyPage:
#     # If page is out of range (e.g. 9999), deliver last page of results.
#         contacts = paginator.page(paginator.num_pages)
#     data = []
#     for con in contacts:
#         marks = con.marks.all();
#         str_marks = ''
#         for mark in marks:
#             str_marks += '<span>' + mark.name + '</span>'
#         i = {"title":con.title,
#              "interest":con.interest,
#              "amount":con.amount_to_invest,
#              "time":con.investTime,
#              "revenue":con.revenue,
#              "benefit":con.benefit,
#              "url":con.url,
#              "is_new":'new' if con.is_new() else '',
#              "marks":str_marks
#         }
#         data.append(i)
#     if data:
#         res['code'] = 1
#     res["pageCount"] = paginator.num_pages
#     res["recordCount"] = item_list.count()
#     res["data"] = data
#     return JsonResponse(res)
# def get_task_page(request):
#     res={'code':0,}
#     page = request.GET.get("page", None)
#     size = request.GET.get("size", 6)
#     filter = request.GET.get("filter", 0)
#     state = request.GET.get("state", 0)
#     try:
#         size = int(size)
#     except ValueError:
#         size = 6
#     if not page or size <= 0:
#         raise Http404
#     item_list = Task.objects.all()
#     filter = str(filter)
#     state = str(state)
#     if filter == '1':
#         item_list = item_list.filter(type='junior')
#     elif filter == '2':
#         item_list = item_list.filter(type='middle')
#     elif filter == '3':
#         item_list = item_list.filter(type='senior')
#     item_list = item_list.filter(state=state)
#     paginator = Paginator(item_list, size)
#     try:
#         contacts = paginator.page(page)
#     except PageNotAnInteger:
#     # If page is not an integer, deliver first page.
#         contacts = paginator.page(1)
#     except EmptyPage:
#     # If page is out of range (e.g. 9999), deliver last page of results.
#         contacts = paginator.page(paginator.num_pages)
#     data = []
#     for con in contacts:
#         money = con.moneyToAdd
#         score = con.scoreToAdd
#         award = ''
#         if money > 0:
#             award += str(money) + u"福币  "
#         if score > 0:
#             award += str(score) + u"积分"
#         i = {"title":con.title,
#              "url":con.url,
#              "time":con.time_limit,
#              "pic":con.pic.url,
#              "view":con.view_count,
#              'provider':con.provider,
#              "is_new":'new' if con.is_new() else '',
#              "num":con.left_num,
#              'award':award,
#         }
#         data.append(i)
#     if data:
#         res['code'] = 1
#     res["pageCount"] = paginator.num_pages
#     res["recordCount"] = item_list.count()
#     res["data"] = data
#     return JsonResponse(res)
# def get_wel_page(request):
#     res={'code':0,}
#     page = request.GET.get("page", None)
#     size = request.GET.get("size", 6)
#     filter = request.GET.get("filter", 0)
#     state = request.GET.get("state", 0)
#     try:
#         size = int(size)
#     except ValueError:
#         size = 6
#     if not page or size <= 0:
#         raise Http404
#     item_list = Welfare.objects.all()
#     filter = str(filter)
#     state = str(state)
#     if filter != '0':
#         item_list = item_list.filter(zero_type=filter)
#     item_list = item_list.filter(state=state)
#     paginator = Paginator(item_list, size)
#     try:
#         contacts = paginator.page(page)
#     except PageNotAnInteger:
#     # If page is not an integer, deliver first page.
#         contacts = paginator.page(1)
#     except EmptyPage:
#     # If page is out of range (e.g. 9999), deliver last page of results.
#         contacts = paginator.page(paginator.num_pages)
#     data = []
#     for con in contacts:
#         i = {"title":con.title,
#              "url":con.url,
#              "time":con.time_limit,
#              "pic":con.pic.url,
#              "view":con.view_count,
#              'provider':con.provider,
#              "is_new":'new' if con.is_new() else '',
#         }
#         data.append(i)
#     if data:
#         res['code'] = 1
#     res["pageCount"] = paginator.num_pages
#     res["recordCount"] = item_list.count()
#     res["data"] = data
#     return JsonResponse(res)
# def get_press_page(request):
#     res={'code':0,}
#     page = request.GET.get("page", None)
#     size = request.GET.get("size", 5)
#     type = request.GET.get("type", 0)
#     try:
#         size = int(size)
#     except ValueError:
#         size = 6
#     if not page or size <= 0:
#         raise Http404
#     item_list = Press.objects.all()
#     type = str(type)
#     if type != '0':
#         item_list = item_list.filter(type=type)
#     paginator = Paginator(item_list, size)
#     try:
#         contacts = paginator.page(page)
#     except PageNotAnInteger:
#     # If page is not an integer, deliver first page.
#         contacts = paginator.page(1)
#     except EmptyPage:
#     # If page is out of range (e.g. 9999), deliver last page of results.
#         contacts = paginator.page(paginator.num_pages)
#     data = []
#     for con in contacts:
#         i = {"title":con.title,
#              "url":con.url,
#              "time":con.pub_date.strftime("%Y-%m-%d"),
#              "view":con.view_count,
#              "summary":con.summary,
#         }
#         data.append(i)
#     if data:
#         res['code'] = 1
#     res["pageCount"] = paginator.num_pages
#     res["recordCount"] = item_list.count()
#     res["data"] = data
#     return JsonResponse(res)
#
#
# def business(request, page=None):
#     if not page:
#         page = 1
#     else:
#         page = int(page)
#     hot_business_list = Company.objects.order_by('-view_count')[0:8]
#     business_list = Company.objects.all()
#     search_key = request.GET.get('key', '')
#     if search_key:
#         business_list = business_list.filter(name__contains=search_key)
#     business_list, page_num = listing(business_list, 36, page)
#     full_path = str(request.get_full_path())
#     path_split = []
#     if 'list-page' in full_path:
#         path_split = re.split('list-page\d+',full_path)
#     elif '?' in full_path:
#         path_split = full_path.split('?')
#         path_split[1] = '?' + path_split[1]
#     else:
#         path_split=[full_path, '']
#     page_dic = {}
#     page_dic['pre_path'] = path_split[0]
#     page_dic['suf_path'] = path_split[1]
#     page_list = []
#     if page_num < 10:
#         page_list = range(1,page_num+1)
#     else:
#         if page < 6:
#             page_list = range(1,8) + ["...",page_num]
#         elif page > page_num - 5:
#             page_list = [1,'...'] + range(page_num-6, page_num+1)
#         else:
#             page_list = [1,'...'] + range(page-2, page+3) + ['...',page_num]
#     page_dic['page_list'] = page_list
#     hot_wel_list = Welfare.objects.filter(is_display=True, state='1').order_by('-view_count')[0:8]
#     content = {
#         'page_dic':page_dic,
#         'hot_business_list':hot_business_list,
#         'business_list':business_list,
#         'hot_wel_list':hot_wel_list,
#     }
#     return render(request, "business.html", content)
#
# def information(request, type=None, page=None, id=None):
#     if not id:
#         if not page:
#             page = 1
#         else:
#             page = int(page)
#         full_path = str(request.get_full_path())
#         path_split = []
#         if 'list-page' in full_path:
#             path_split = re.split('list-page\d+',full_path)
#         elif '?' in full_path:
#             path_split = full_path.split('?')
#             path_split[1] = '?' + path_split[1]
#         else:
#             path_split=[full_path, '']
#         page_dic = {}
#         ref_dic = {}
#         page_dic['pre_path'] = path_split[0]
#         page_dic['suf_path'] = path_split[1]
#         info_list = Information.objects.filter(is_display=True)
#         state = request.GET.get('state', '1')
#         full_path_ = re.sub(r'/list-page\d+&?', '', full_path, 1)
#         ref_path1 = re.sub(r'state=\d+&?', '', full_path_, 1)
#         ref_path2, num = re.subn(r'state=\d+', 'state=2', full_path_)
#         if num == 0:
#             if '?' in ref_path2:
#                 ref_path2 += '&state=2'
#             else:
#                 ref_path2 += '?state=2'
#         if ref_path1[-1] == '?' or ref_path1[-1] == '&':
#             ref_path1 = ref_path1[:-1]
#         ref_dic = {'state':state, 'ref_path1':ref_path1, 'ref_path2':ref_path2,}
#         if type:
#             type = str(type)
#             info_list = info_list.filter(type=type)
#         info_list, page_num = listing(info_list, 6, int(page))
#         if page_num < 10:
#             page_list = range(1,page_num+1)
#         else:
#             if page < 6:
#                 page_list = range(1,8) + ["...",page_num]
#             elif page > page_num - 5:
#                 page_list = [1,'...'] + range(page_num-6, page_num+1)
#             else:
#                 page_list = [1,'...'] + range(page-2, page+3) + ['...',page_num]
#         page_dic['page_list'] = page_list
#         hot_info_list = Information.objects.filter(is_display=True).order_by('-view_count')[0:10]
#         hot_wel_list = Welfare.objects.order_by('-view_count')[0:10]
#         ad_list = Advertisement.objects.filter(Q(location='0')|Q(location='10'),is_hidden=False)[0:8]
#         context = {
#             'info_list':info_list,
#             'page_dic':page_dic,
#             'hot_info_list':hot_info_list,
#             'hot_wel_list':hot_wel_list,
#             'type':type,
#             'ad_list':ad_list,
#         }
#         return render(request, 'information.html', context)
#     elif id:
#         id = int(id)
#         info = None
#         try:
#             info = Information.objects.get(id=id)
#         except Information.DoesNotExist:
#             raise Http404(u"该页面不存在")
#         update_view_count(info)
#         hot_info_list = Information.objects.filter(is_display=True).order_by('-view_count')[0:6]
#         return render(request, 'detail-information.html',{'info':info, 'hot_info_list':hot_info_list, 'type':'Information'})
#
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
