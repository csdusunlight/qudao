#coding:utf-8
'''
Created on 20160608

@author: lch
'''
import logging
from wafuli_admin.management.commands.capture import load_gzh, isWindowsSystem
from wafuli.models import Hongbao, Company
from django.core.urlresolvers import reverse
import time
logger=logging.getLogger('wafuli')
from django.core.management.base import BaseCommand
from wafuli_admin.models import Gongzhonghao




class Command(BaseCommand):
    def handle(self, *args, **options):
        logger.info("******Capture Tasks is beginning*********")
        begin_time = time.time()
        gzh_list = Gongzhonghao.objects.filter(is_on=True)
        company = Company.objects.get(name=u"免费福利")
        for gzh in gzh_list:
            name = gzh.name.encode('utf-8')
            contents = load_gzh(name)
#             if not contents:
#                 if isWindowsSystem():
#                     name = name.decode('utf-8').encode('gbk')
            logger.info(name + "的抓取条数：" + str(len(contents) if not contents is None else None))
            if not contents:
                continue
            for con in contents:
                wel = Hongbao.objects.create(type='hongbao',title=con['title'],state='0',company=company,strategy=con['content'], pic = con['pic_download'])
                wel.url = reverse('welfare', kwargs={'id': wel.id})
                wel.save(update_fields=['url'])
#         company = Company.objects.get(name=u"免费福利")
#         contents = load_gzh()
#         for con in contents:
#             wel = Hongbao.objects.create(type='hongbao',title=con['title'],state='1',company=company,strategy=con['content'], pic = con['pic_download'])
#             wel.url = reverse('welfare', kwargs={'id': wel.id})
#             wel.save(update_fields=['url'])
# #             Hongbao.objects.create(welfare_ptr_id=wel.id)
        end_time = time.time()
        logger.info("******Capture Tasks is finished*********time:%s*********",end_time-begin_time)