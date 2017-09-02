var sendTelVerifyCodeImageV = function(phoneNum, action, actionurl, hashkey, response) {
	$.ajax({
		url : actionurl,
		async : false,
		data : {
			'phone' : phoneNum,
			'action' : action,
			'hashkey': $("#id_hashkey").val(),
			'response': $("#x_yanzhengma").val(),
			},
		dataType : 'json',
		timeout : 3000,
		success : function(data) {
			if (data.code == '1') {
				alert('验证码发送成功！');						
			} else {								
				alert(data.message);
			}
		},
		error : function() {
			alert("网络异常，请检查网络。");
			}
	});
};