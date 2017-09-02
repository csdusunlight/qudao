$(function() {
	var telpig = true;//事件点击通道
	var emailpig = true;//事件点击通道
	/*****************************发送验证码：手机**************************************/

	var sendTelVerifyCodeImageV = function(phoneNum, action, actionurl) {
		if(telpig){
			$.ajax({
				url : actionurl,
				async : false,
				data : {
					'phone' : phoneNum,
					'action' : action,
					// 'hashkey': $("#id_hashkey").val(),
					// 'response': $("#x_yanzhengma").val(),
					},
				dataType : 'json',
				timeout : 3000,
				success : function(data) {
					if (data.code == '1') {
						alert('验证码发送成功！');
					} else {
						alert(data.message);
						// if (action=='register'){
						// 	var new_cptch_key = data['key'];
					 //        var new_cptch_image = data['image_url'];
					 //        key = $("#id_hashkey");
					 //        img = $("#id_checkImg");
					 //        key.attr("value", new_cptch_key);
					 //        img.attr("src", new_cptch_image);
						// }
						if (action=='change_bankcard'){

						}
					}
				},
				error : function() {
					alert("网络异常，请检查网络。");
				}
			});
		}
	};
	/*****************************发送验证码：邮箱**************************************/
	var sendEmailVerifyCode = function(phoneNum, action, actionurl) {
		if(emailpig){
			$.ajax({
				url : actionurl,
				async : false,
				data : {
					'model' : phoneNum,
					'action' : action
				},
				dataType : 'json',
				timeout : 3000,
				success : function(data) {
					if (data.code == '1') {
						alert('验证码发送成功！');
						send_sms_event_mail = setInterval(control_sendmail,1000);
					} else {
						alert(data.message);
					}
				},
				error : function() {
					alert("网络异常，请检查网络。");
				}
			});
		}
	};


/*****************************时间动态切换***********************************/
	/**
	 * 时间切换方法：手机
	 */
	var send_sms_time = 180;
	var send_sms_event;
	function control_send() {
		telpig=false;
		if (send_sms_time == 0) {
			send_sms_time = 180;
			$('#action-send-code').html('获取验证码');
			clearInterval(send_sms_event);
			telpig = true;
			return;
		}
		$('#action-send-code').html(send_sms_time + '秒后可重发');
		send_sms_time -= 1;
	}
	var send_sms_time_old = 180;
	var send_sms_event_old;
	function control_send_old() {
		if (send_sms_time_old == 0) {
			send_sms_time_old = 180;
			$('#action-send-code-old').html('获取验证码');
			clearInterval(send_sms_event_old);
			telpig = true;
			return;
		}
		$('#action-send-code-old').html(send_sms_time_old + '秒后可重发');
		send_sms_time_old -= 1;
	}

	/**
	 * 绑定点击方法：手机发送验证码校验图片验证
	 */
	$('#action-send-code-imagvalidate').bind('click',function() {
		if(is_tel($("input[name='mobile']"))){
		}
		else{
			// if(is_net_code($("#x_yanzhengma"))){}
			// else{
			phoneNum = $("input[name='mobile']").val();
			actionType = 'register';
			actionurl = get_code_url;
			sendTelVerifyCodeImageV(phoneNum, actionType, actionurl);
		// }
		}

	});
	$('#yanzhengma_button').bind('click',function() {
		actionType = "change_bankcard";
		actionurl = get_code_url;
		phoneNum = phoneNum;
		sendTelVerifyCodeImageV(phoneNum, actionType, actionurl);
	});

});
