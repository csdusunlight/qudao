#coding:utf-8
'''
Created on 2018年4月19日

@author: lch
'''
from alipay import AliPay
import time
from finance.models import ZhifubaoTransferLog
from django.conf import settings
from os import path as ospath
app_pri_key_file_fulio = ospath.join(settings.CONFIG_DIR, "app_pri_key_fulio.pem")
ali_pub_key_file_fulio = ospath.join(settings.CONFIG_DIR, "ali_pub_key_fulio.pem")
app_pri_key_file_wafuli = ospath.join(settings.CONFIG_DIR, "app_pri_key_wafuli.pem")
ali_pub_key_file_wafuli = ospath.join(settings.CONFIG_DIR, "ali_pub_key_wafuli.pem")
alipay_fulio = None
alipay_wafuli = None
if ospath.exists(app_pri_key_file_fulio) and ospath.exists(ali_pub_key_file_fulio):
    app_private_key_string = open(ospath.join(settings.CONFIG_DIR, "app_pri_key_fulio.pem")).read()
    alipay_public_key_string = open(ospath.join(settings.CONFIG_DIR, "ali_pub_key_fulio.pem")).read()
    try:
        alipay_fulio = AliPay(
              appid="2018062660469113",
              app_notify_url=None,  # the default notify path
              app_private_key_string=app_private_key_string, 
              alipay_public_key_string=alipay_public_key_string,  # alipay public key, do not use your public key!
              sign_type="RSA2", # RSA or RSA2
              debug=False  # False by default
        )
    except:
        pass
if ospath.exists(app_pri_key_file_wafuli) and ospath.exists(ali_pub_key_file_wafuli):
    app_private_key_string = open(ospath.join(settings.CONFIG_DIR, "app_pri_key_wafuli.pem")).read()
    alipay_public_key_string = open(ospath.join(settings.CONFIG_DIR, "ali_pub_key_wafuli.pem")).read()
    try:
        alipay_wafuli = AliPay(
              appid="2018041860005082",
              app_notify_url=None,  # the default notify path
              app_private_key_string=app_private_key_string,
              alipay_public_key_string=alipay_public_key_string,  # alipay public key, do not use your public key!
              sign_type="RSA2", # RSA or RSA2
              debug=False  # False by default
        )
    except:
        pass

def batch_transfer_to_zhifubao(account_list, payer='wafuli'):
    ret_list = []
    suc_num = 0
    objs = []
    ret = {}
    for account in account_list:
        timestamp = time.time()
        payee_account=account.get('payee_account')
        payee_real_name=account.get('payee_real_name')
        amount=account.get('amount')
        remark=account.get('remark') or u"福利联盟提现"
        alipay = globals().get('alipay_%s' % payer)
        if not alipay:
            raise Exception(u'不存在的支付宝账号：%s' % payer)
        result = alipay.api_alipay_fund_trans_toaccount_transfer(
            str(int(timestamp * 1000)),
            payee_type="ALIPAY_LOGONID",
            payee_account=payee_account,
            payee_real_name=payee_real_name,
            amount=amount,
            remark=remark
        )
        
        print 'start'
        print result
        msg = result['msg']
        if msg == 'Success':
            suc_num += 1
        else:
            account['msg'] = result['sub_msg']
            ret_list.append(account)
        obj = ZhifubaoTransferLog(result=msg, payee_account=payee_account, 
                                  payee_real_name=payee_real_name, amount=amount)
        objs.append(obj)
    ZhifubaoTransferLog.objects.bulk_create(objs)
    ret['suc_num'] = suc_num
    ret['detail'] = ret_list
    return ret

if __name__ == '__main__':
    # function_name = "alipay_" + alipay_function_name.replace(".", "_")
    ret = batch_transfer_to_zhifubao([{'payee_account':"18500581509",'payee_real_name':u'吕春晖','amount':0.1}])
    ret = batch_transfer_to_zhifubao([{'payee_account':"18500581509",'payee_real_name':u'吕春晖','amount':0.1}],'fulio')
    print ret