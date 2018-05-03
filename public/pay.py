#coding:utf-8
'''
Created on 2018年4月19日

@author: lch
'''
from alipay import AliPay
import datetime
app_private_key_string = open("../dragon/app_pri_key.pem").read()
alipay_public_key_string = open("../dragon/ali_pub_key.pem").read()

print app_private_key_string, alipay_public_key_string
alipay = AliPay(
      appid="2018041860005082",
      app_notify_url=None,  # the default notify path
      app_private_key_string=app_private_key_string, 
      alipay_public_key_string=alipay_public_key_string,  # alipay public key, do not use your public key!
      sign_type="RSA2", # RSA or RSA2
      debug=False  # False by default
)

if __name__ == '__main__':
    # function_name = "alipay_" + alipay_function_name.replace(".", "_")
    result = alipay.api_alipay_fund_trans_toaccount_transfer(
            datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
            payee_type="ALIPAY_LOGONID",
            payee_account="18500581509",
            payee_real_name=u'吕春晖',
            amount=0.1
        )
    return result