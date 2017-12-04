'''
Created on 20161225

@author: lch
'''
from django.conf.urls import url,include
from django.views.generic.base import TemplateView

urlpatterns = [
    url(r'^$', 'weixin.views.weixin', name='token_verify'),
    url(r'^bind-user/$', 'weixin.views.bind_user', name='bind-user'),
    url(r'^bind-user/setpasswd/$', 'weixin.views.bind_user_setpasswd', name='bind-user-setpasswd'),
    url(r'^bind-user/success/$', 'weixin.views.bind_user_success', name='bind-user-success'),
    url(r'^bind-user/auditing/$', TemplateView.as_view(template_name='m_bind_auditing.html')),
    url(r'^bind-user/nouser/$', TemplateView.as_view(template_name='m_bind_nouser.html')),
#     url(r'^slider/$', 'app.views.get_slider', name='app_slider'),
#     url(r'^recom/$', 'app.views.get_recom', name='app_recom'),
#     url(r'^detail/hongbao/$', 'app.views.get_content_hongbao', name='detail_hb'),
#     url(r'^detail/youhuiquan/$', 'app.views.get_content_youhuiquan', name='detail_yhq'),
#     url(r'^obtain_youhuiquan/$', 'app.views.exp_welfare_youhuiquan', name='obtain_youhuiquan'),
#     
#     url(r'^login/$', 'app.views.login', name='login'),
#     url(r'^user/$', 'app.views.get_user_info', name='user_info'),
]
