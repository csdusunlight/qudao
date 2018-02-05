#coding:utf-8
'''
Created on 2018年2月1日

@author: lch
'''
from django.conf import settings
from django.core.cache import cache
import json


#read cache user id
def read_from_cache(key):
    value = cache.get(key)
    print value
    if value == None:
        data = None
    else:
        data = json.loads(value)
    return data

#write cache user id
def write_to_cache(key, value, expire=settings.NEVER_REDIS_TIMEOUT):
    cache.set(key, json.dumps(value), expire)

def cache_incr_or_set(key, n=1):
    if cache.has_key(key):
        cache.incr(key, n)
    else:
        cache.set(key, n, 24*60*60)
        
def cache_decr_or_set(key, n=1):
    if cache.has_key(key):
        cache.decr(key, n)
    else:
        cache.set(key, 0, 24*60*60)
    
if __name__ == '__main__':
    print json.dumps('sedfsd')