#coding:utf-8
'''
从大淘客http://demo.dataoke.com/ 抓取：领券秒杀 和 9块9包邮

written by  lch
'''
import cookielib
import urllib
import urllib2
import logging
import re

from bs4 import BeautifulSoup
from django.core.management import BaseCommand
from django.db import transaction

from wafuli.models import Fuligou

url = 'http://fuligou.wafuli.cn'
url_nine = 'http://fuligou.wafuli.cn/index.php?r=nine&u=699467'
logger = logging.getLogger('wafuli')

class Browser(object):
    cookie = cookielib.CookieJar()
    handler = urllib2.HTTPCookieProcessor(cookie)
    opener = urllib2.build_opener(handler)
    def get(self,url):
        request = urllib2.Request(url)
    #     request.add_header('Accept-encoding', 'gzip')
        request.add_header('User-Agent','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36')
        return self.open(request)
    def post(self, url, postData, headers):
        data = urllib.urlencode(postData)
        # 生成post数据 ?key1=value1&key2=value2的形式
        request = urllib2.Request(url, data, headers)
        return self.open(request)
    def open(self, request):
        result = ''
        try:
            response = Browser.opener.open(request)
#             buf = StringIO(response.read())
#             f = gzip.GzipFile(fileobj=buf)
            data = response.read()
#             result = response.read()
        # 由于该网页是gb2312的编码，所以需要解码
#             print result
        # 打印登录后的页面
        except urllib2.HTTPError, e:
            print e.code
        return data
def updateFuligou():
    browser = Browser()
    allhtml = browser.get(url)
    soup = BeautifulSoup(allhtml, "html.parser")
    a=soup.find("div", class_="discount")
    # print a.prettify()
    b=a.find_all("div", class_="pro_detail")
    new_list = []
    for item in b:
        olddiv = item.find("div", class_="old-price")
        old_price = olddiv.p.text.strip()[1:]
        old_price = float(old_price)
        newdiv = item.find("div", class_="buy-price")
        buy_price = newdiv.text.strip()
        buy_price = float(buy_price)
        # coupin_value = old_price - buy_price
        img_src = item.img['src'].strip()
        href = url + item.a['href']
        title = item.p.a.text.strip()
        f = Fuligou(is_main=True, title=title, buy_price=buy_price, old_price=old_price,
                    img_src=img_src, href=href)
        new_list.append(f)
    allhtml = browser.get(url_nine)
    soup = BeautifulSoup(allhtml, "html.parser")
    good_list = soup.find('div', class_='goods-list').find_all('li')
    for i in range(5):
        item = good_list[i]
        href = url + re.sub('\s', '', item.a['href'])
        img_src = item.img['src']
        buy_price = item.find('span', class_='price').b.text.strip()[1:]
        old_price = item.find('span', class_='old-price').text.strip()[1:]
        buy_price = float(buy_price)
        old_price = float(old_price)
        # coupin_value = old_price - buy_price
        title = item.find('div',class_='title').a.text.strip()
        f = Fuligou(is_main=False, title=title, buy_price=buy_price, old_price=old_price,
                    img_src=img_src, href=href)
        new_list.append(f)
    with transaction.atomic():
        Fuligou.objects.all().delete()
        Fuligou.objects.bulk_create(new_list)

class Command(BaseCommand):
    def handle(self, *args, **options):
        logger.info("******Capture Fuligou is beginning*********")
        updateFuligou()
        logger.info("******Capture Fuligou is finished*********")