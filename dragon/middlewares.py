'''
Created on 20170919

@author: lch
'''
from django.http.response import Http404
from account.models import MyUser
class SubdomainMiddleware(object):
    def process_request(self, request):
        domain_parts = request.get_host().split('.')
        if len(domain_parts) == 3:
            username = domain_parts[0]
            try:
                request.user = MyUser.objects.get(username=username)
            except:
                pass
        return None