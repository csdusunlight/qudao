# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from DjangoUeditor.models import UEditorField
from django.core.urlresolvers import reverse
from django.utils import timezone
IS_HOT = (
    ('0', u'热门'),
    ('1', u'不热门'),
)
IS_CAOGAO = (
    ('0', u'草稿'),
    ('1', u'非草稿'),
)

@python_2_unicode_compatible
class Tag(models.Model):
    tname = models.CharField('标签名称', max_length=256)
    tintro = models.TextField('标签简介', default='')

    def get_absolute_url(self):
        return reverse('tags')

    def __str__(self):
        return self.tname

    class Meta:
        verbose_name = '标签'
        verbose_name_plural = '标签'
        ordering = ['tname']  # 排序


class Agroup(models.Model):
    agname=models.CharField('分组名称', max_length=256)   #分组和文章是一对多
    class Meta:
        verbose_name = '分组'
        verbose_name_plural = '分组'


class Article(models.Model):
    agroup = models.ForeignKey(Agroup,verbose_name="分类分组")
    atag = models.ManyToManyField(Tag, verbose_name='分类标签')
    apic = models.ImageField(upload_to='photos/%Y/%m/%d', verbose_name=u"标志图片上传（最大不超过30k，越小越好）",blank=False)
    atitle = models.CharField('标题',unique=True, max_length=200)
    aslug = models.CharField('网址', max_length=256, db_index=True)
    aseo_title = models.CharField(max_length=200, verbose_name=u"SEO标题", blank=True)
    aseo_keywords = models.CharField(max_length=200, verbose_name=u"SEO关键词", blank=True)
    aseo_description = models.CharField(max_length=200, verbose_name=u"SEO描述", blank=True)
    apub_date = models.DateTimeField('发表时间',default=timezone.now)
    aupdate_time = models.DateTimeField('更新时间', auto_now=True,null=True)
    ais_published = models.CharField('是否草稿',choices=IS_CAOGAO,null=True,max_length=2)
    ais_hot = models.CharField('是否热门文章',choices=IS_HOT,null=True,max_length=2)
    acontent =UEditorField(u"文章内容", width=900, height=300,
                     imagePath="photos/%(year)s/%(month)s/%(day)s/",
                     filePath="photos/%(year)s/%(month)s/%(day)s/",
                     upload_settings={"imageMaxSize":120000},settings={},command=None,blank=True)


    def get_absolute_url(self):
        return reverse('article')


    class Meta:
        verbose_name = '资讯'
        verbose_name_plural = '资讯'


class Url(models.Model):
    uname=models.CharField('链接名称', max_length=256)   #分组和文章是一对多
    url=models.CharField('链接具体', max_length=256)   #分组和文章是一对多
    upub_date = models.DateTimeField('发表时间',default=timezone.now)
    class Meta:
        verbose_name = '链接'
        verbose_name_plural = '链接'