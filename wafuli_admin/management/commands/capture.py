#coding:utf-8
'''
Created on 20160608

@author: lch
'''
import logging
from wafuli.models import Hongbao, Company
import urllib2
from StringIO import StringIO
from bs4 import BeautifulSoup
import gzip
import re
import urllib
import cookielib
import time,os
from dragon.settings import MEDIA_ROOT
from django.core.urlresolvers import reverse
import datetime
from django.core.management.base import BaseCommand
from PIL import Image
from wafuli_admin.management.commands.ruokuai import APIClient
host = 'http://mp.weixin.qq.com'
logger=logging.getLogger('django')
today =datetime.date.today().strftime("%Y-%m-%d")
todaydir = os.path.join(MEDIA_ROOT, 'capfromweixin', today).replace('\\','/')
url_pre = '/media/capfromweixin/' + today + '/'
if not os.path.exists(todaydir):
    os.makedirs(todaydir)
import platform
 
def isWindowsSystem():
    return 'Windows' in platform.system()
class Browser(object):
    cookie = cookielib.CookieJar()
    handler = urllib2.HTTPCookieProcessor(cookie)
    opener = urllib2.build_opener(handler)
    def get(self,url):
#         logger.info("geturl:" + url)
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
        data = None
        try:
            response = Browser.opener.open(request, timeout=5)
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
    
def getimgcode(imagePath, typeid):
    client = APIClient()
    result = ''
    paramDict = {}
    paramDict['username'] = 'boy28930'
    paramDict['password'] = 'pl6561066'
    paramDict['typeid'] = typeid
    paramDict['timeout'] = 60
    paramDict['softid'] = 1
    paramDict['softkey'] = 'b40ffbee5c1cf4e38028c197eb2fc751'
    paramKeys = ['username',
         'password',
         'typeid',
         'timeout',
         'softid',
         'softkey'
        ]
#     imagePath = 'e:\image.jpeg'
    img = Image.open(imagePath)
    if img is None:
        logger.error('get file error!')
        return None
    img.save("upload.gif", format="gif")
    filebytes = open("upload.gif", "rb").read()
    result = client.http_upload_image("http://api.ruokuai.com/create.xml", paramKeys, paramDict, filebytes)
    match = re.search(r'<Result>(\S*)</Result>',result)
    result = match.group(1)
    return result
def load_gzh(name):
    logger.info(name + "is beginning to load...")
    browser = Browser()
    burl = 'http://weixin.sogou.com/weixin?type=1&s_from=input&query='+name+'&ie=utf8&_sug_=n&_sug_type_='
#     logger.error('http://weixin.sogou.com/weixin?type=1&s_from=input&query=券妈妈&ie=utf8&_sug_=n&_sug_type_=')
    page = browser.get(burl)
    if page.find('请输入验证码') != -1:
        tc = time.time()
        tc = tc*1000
        CaptchaUrl = "http://weixin.sogou.com/antispider/util/seccode.php?tc=" + str(tc)
        PostUrl = "http://weixin.sogou.com/antispider/thank.php"
        
        picture = browser.get(CaptchaUrl)
        # 用openr访问验证码地址,获取cookie
        imgname = os.path.join(todaydir, 'vericode.jpg').replace('\\','/')
        local = open(imgname, 'wb')
        local.write(picture)
        local.close()
        # 保存验证码到本地
        SecretCode = getimgcode(imgname, 3060)#raw_input('input code::')
        logger.error('secretcode'+ SecretCode)
        # 打开保存的验证码图片 输入
        postData = {
            'c': SecretCode,
            'r': burl,
            'v':5
        }
        # 根据抓包信息 构造表单
        headers = {
            'Accept': '*/*',
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36',
            'Host':'weixin.sogou.com',
            'Origin':'http://weixin.sogou.com/',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'X-Requested-With':'XMLHttpRequest',
        }
        # 根据抓包信息 构造headers
        # 生成post数据 ?key1=value1&key2=value2的形式
        # 构造request请求
        result = browser.post(PostUrl, postData, headers)

        logger.error(name + "sougou antispider")
        return None
#        page = browser.get(burl)
        
	print page
    soup = BeautifulSoup(page,"html.parser")
    news_box = soup.find("div", class_="news-box")
    try:
        gongzhonghao = news_box.a['href']
    except:
        if isWindowsSystem():
            name = name.decode('utf-8').encode('gbk')
        logger.error("no gzh found named" + name )
        logger.error(burl)
        print soup.prettify()
        return None
    article_list_html = browser.get(gongzhonghao)
    if article_list_html.find('请输入验证码') != -1:
        cert = time.time()
        cert = cert*1000
        CaptchaUrl = "http://mp.weixin.qq.com/mp/verifycode?cert=" + str(cert)
        PostUrl = "http://mp.weixin.qq.com/mp/verifycode"
        
        picture = browser.get(CaptchaUrl)
        # 用openr访问验证码地址,获取cookie
        imgname = os.path.join(todaydir, 'vericode.jpg').replace('\\','/')
        local = open(imgname, 'wb')
        local.write(picture)
        local.close()
        # 保存验证码到本地
        SecretCode = getimgcode(imgname, 2040)#raw_input('input code::')
        logger.error(SecretCode)
        # 打开保存的验证码图片 输入
        postData = {
            'input': SecretCode,
            'cert': cert,
        }
        # 根据抓包信息 构造表单
        headers = {
            'Accept': '*/*',
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36',
            'Host':'mp.weixin.qq.com',
            'Origin':'http://mp.weixin.qq.com',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'X-Requested-With':'XMLHttpRequest',
        }
        # 根据抓包信息 构造headers
        # 生成post数据 ?key1=value1&key2=value2的形式
        # 构造request请求
        result = browser.post(PostUrl, postData, headers)
        article_list_html = browser.get(gongzhonghao)

    soup = BeautifulSoup(article_list_html,"html.parser")
#     print soup.prettify(encoding='')
    matchObj = re.findall("\"list\":(\[.*\])", soup.prettify())

    day_list = []
    if matchObj:
        day_list = eval(matchObj[0])
    else:
        logger.info("no list")
        return None
    if day_list:
        today_list = day_list[0]['app_msg_ext_info']
        msg_item_list = day_list[0]['app_msg_ext_info']['multi_app_msg_item_list']
        #最新文章在列表中是独立列出的
        msg_item_list.insert(0, {'content_url':today_list['content_url'], 'cover':today_list['cover']})
    else:
        logger.info('day_list is empty')
        return None
    article_urls = []
    pics=[]
    for msg in msg_item_list:
        url = host+msg['content_url']
        url = url.replace('amp;','')
        article_urls.append(url)
        pics.append(msg['cover'])
#     print 'article_urls',article_urls
    contents = []
    t = 0
    for url in article_urls:
        article_page = browser.get(url)
        soup = BeautifulSoup(article_page,"html.parser")
        datestr = soup.find(id="post-date").string.strip()
        todaystr =datetime.date.today().strftime("%Y-%m-%d")
        if datestr!=todaystr:
            logger.info(name + '今天没有新闻')
            return None
        div = soup.find("div",class_="rich_media_content")
        if div:
            rich_content = unicode(div).replace("data-src","src")
            title = soup.h2.string.strip()
        else:
            rich_content = u"没有内容"
            title = u"无"
        if not Hongbao.objects.filter(state__in=['0','1'], title=title).exists():
            contents.append({'title':title, 'content':rich_content, 'picture':pics[t]})
        t += 1
    for c in contents:
        url = c['picture']
        title_pre = c['title'][:3].replace('/', '')
        sub = re.findall("wx_fmt=([a-z]+)", url)
        stype = sub[0] if sub else 'jpg'
        picture = browser.get(url)
#         cert = time.time()
#         cert = int(cert*1000)
        filename = title_pre + '.' + stype
        file_path = os.path.join(todaydir, filename).replace('\\','/')
        local = open(file_path, 'wb')
        local.write(picture)
        local.close()
        c['pic_download'] = url_pre + filename
        content = c['content']
        soup = BeautifulSoup(content,"html.parser")
        imglist = soup.find_all('img') 
        length = len(imglist)  #计算集合的个数  
        for i in range(length):  
            url = imglist[i].attrs['src']
#             print url
            sub = re.findall("wx_fmt=([a-z]+)", url)
#             print sub
            stype = 'jpg'
            if sub:
                stype = sub[0]
            picture = browser.get(url)
    #         cert = time.time()
    #         cert = int(cert*1000)
            filename = title_pre + str(i) + '.' + stype
            file_path = os.path.join(todaydir, filename).replace('\\','/')
            local = open(file_path, 'wb')
            local.write(picture)
            local.close()
            locate_url = url_pre + filename
            content = content.replace(url, locate_url)
        c['content'] = content
    return contents
class Command(BaseCommand):
    help = 'input gongzhaohao name'
    def add_arguments(self, parser):
        parser.add_argument('name', nargs='+')
    def handle(self, *args, **options):
        company = Company.objects.get(name=u"免费福利")
        name=options['name'][0]
        print name
        if isWindowsSystem():
            name = name.decode('gbk').encode('utf-8')
        contents = load_gzh(name)
        for con in contents:
            wel = Hongbao.objects.create(type='hongbao',title=con['title'],state='0',company=company,strategy=con['content'], pic = con['pic_download'])
            wel.url = reverse('welfare', kwargs={'id': wel.id})
            wel.save(update_fields=['url'])
#             Hongbao.objects.create(welfare_ptr_id=wel.id)
        logger.info("******Invite_charge is finished*********")
        
if __name__ == '__main__':
    browser=Browser()
    burl = 'http://weixin.sogou.com/weixin?type=1&s_from=input&query=券妈妈&ie=utf8&_sug_=n&_sug_type_='
#     logger.error('http://weixin.sogou.com/weixin?type=1&s_from=input&query=券妈妈&ie=utf8&_sug_=n&_sug_type_=')
    page = browser.get(burl)
    if page.find('请输入验证码') != -1:
        tc = time.time()
        tc = tc*1000
        CaptchaUrl = "http://weixin.sogou.com/antispider/util/seccode.php?tc=" + str(tc)
        PostUrl = "http://weixin.sogou.com/antispider/thank.php"
        
        picture = browser.get(CaptchaUrl)
        # 用openr访问验证码地址,获取cookie
        imgname = os.path.join(todaydir, 'vericode.jpg').replace('\\','/')
        local = open(imgname, 'wb')
        local.write(picture)
        local.close()
        # 保存验证码到本地
        SecretCode = getimgcode(imgname, 3060)#raw_input('input code::')
#         logger.error(SecretCode)
        # 打开保存的验证码图片 输入
        postData = {
            'c': SecretCode,
            'r': burl,
            'v':5
        }
        # 根据抓包信息 构造表单
        headers = {
            'Accept': '*/*',
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36',
            'Host':'mp.weixin.qq.com',
            'Origin':'http://mp.weixin.qq.com',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'X-Requested-With':'XMLHttpRequest',
        }
        # 根据抓包信息 构造headers
        # 生成post数据 ?key1=value1&key2=value2的形式
        # 构造request请求
        result = browser.post(PostUrl, postData, headers)
        print result
        page = browser.get(burl)
    soup = BeautifulSoup(page,"html.parser")
    print soup.prettify()