# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from DjangoUeditor.models import UEditorField
from django.core.urlresolvers import reverse


@python_2_unicode_compatible
class Tag2(models.Model):
    tname = models.CharField('标签名称', max_length=256)
    tslug = models.CharField('标签网址', max_length=256, db_index=True)
    tintro = models.TextField('标签简介', default='')

    def get_absolute_url(self):
        return reverse('tags', args=(self.slug, ))

    def __str__(self):
        return self.tname

    class Meta:
        verbose_name = '标签'
        verbose_name_plural = '标签'
        ordering = ['tname']  # 排序


@python_2_unicode_compatible
class Article2(models.Model):
    #Atag = models.ManyToManyField(Tag2, verbose_name='分类标签')
    Atitle = models.CharField('标题', max_length=256)
    Aslug = models.CharField('网址', max_length=256, db_index=True)

    Acontent = models.TextField('内容', default='', blank=True)
    Apub_date = models.DateTimeField('发表时间', auto_now_add=True, editable=True)
    Aupdate_time = models.DateTimeField('更新时间', auto_now=True, null=True)
    Acontent1 = UEditorField('内容1', height=40, width=200,default=u'test', blank=True, imagePath="uploads/images/",\
        toolbars='besttome')

    #Apublished = models.BooleanField('正式发布', default=True)

    def get_absolute_url(self):
        return reverse('article', args=(self.Aslug, ))

    def __str__(self):
        return self.Atitle

    class Meta:
        verbose_name = '教程'
        verbose_name_plural = '教程'