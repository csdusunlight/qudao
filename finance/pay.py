#coding:utf-8
'''
Created on 2018年4月19日

@author: lch
'''
from alipay import AliPay
import datetime
from finance.models import ZhifubaoTransferLog
from django.conf import settings
from os import path as ospath
app_private_key_string = open(ospath.join(settings.CONFIG_DIR, "app_pri_key.pem")).read()
alipay_public_key_string = open(ospath.join(settings.CONFIG_DIR, "ali_pub_key.pem")).read()

print app_private_key_string, alipay_public_key_string
alipay = AliPay(
      appid="2018041860005082",
      app_notify_url=None,  # the default notify path
      app_private_key_string=app_private_key_string, 
      alipay_public_key_string=alipay_public_key_string,  # alipay public key, do not use your public key!
      sign_type="RSA2", # RSA or RSA2
      debug=False  # False by default
)

def batch_transfer_to_zhifubao(account_list):
    ret_list = []
    suc_num = 0
    objs = []
    ret = {}
    for account in account_list:
        payee_account=account.get('payee_account')
        payee_real_name=account.get('payee_real_name')
        amount=account.get('amount')
        result = alipay.api_alipay_fund_trans_toaccount_transfer(
            datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
            payee_type="ALIPAY_LOGONID",
            payee_account=payee_account,
            payee_real_name=payee_real_name,
            amount=amount
        )
        msg = result['msg']
        if msg == 'Success':
            suc_num += 1
        else:
            account['msg'] = msg
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
    ret = batch_transfer_to_zhifubao([{'payee_account':"18500581509",'payee_real_name':u'吕春晖','amount':0.1},
                                {'payee_account':"18500581509",'payee_real_name':u'吕晖','amount':0.1}])
    print ret