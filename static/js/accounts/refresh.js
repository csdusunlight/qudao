


// function is_username(obj, checkUsed) {
// 	if (obj.val() == '') {
// 		divname.innerHTML='<font class="tips_false">请输入用户名</font>';
// 		obj.css("border-color","#f01e32");
// 		return true;
// 	} else if (!validateUserName(obj.val())) {
// 		divname.innerHTML='<font class="tips_false">用户名格式不符</font>';
// 		obj.css("border-color","#f01e32");
// 		return true;
// 	}else {
// 		if(checkUsed) {
// 			validateUsedUsername(obj.val(),true,obj);
// 		}
// 		return false;
// 	}
// }


		//验证用户是否重复 username：用户名   asy：false同步  true异步
// function validateUsedUsername(name,asy,obj){
// 	if(asy!=false){
// 		asy = true;
// 	}
// 	var isUsed = true;
// 	$.ajax({
// 		url : verifyusername_url,
// 		data : {
// 			'username' : name
// 		},
// 		dataType : 'json',
// 		async : asy,
// 		success : function(data) {
// 			if(asy){
// 				if (data.code == '1') {
// 					divname.innerHTML='<font class="tips_true"></font>';
// 				}else{
// 					divname.innerHTML='<font class="tips_false">该用户名已注册</font>';
// 				}
// 			}else{
// 				if (data.code == '1') {
// 					isUsed=true;
// 				} else {
// 					isUsed=false;
// 				}
// 			}
// 		}
// 	});
// 	return isUsed;
// }
// function validateUsedEmail(email,asy,obj){
// 	if(asy!=false){
// 		asy = true;
// 	}
// 	var isUsed = true;
// 	$.ajax({
// 		url : verifyemail_url,
// 		data : {
// 			'email' : email
// 		},
// 		dataType : 'json',
// 		async : asy,
// 		success : function(data) {
// 			if(asy){
// 				if (data.code == '1') {
// 					divmail.innerHTML='<font class="tips_true"></font>';
// 				}else{
// 					divmail.innerHTML='<font class="tips_false">该邮箱已注册</font>';
// 				}
// 			}else{
// 				if (data.code == '1') {
// 					isUsed=true;
// 				} else {
// 					isUsed=false;
// 				}
// 			}
// 		}
// 	});
// 	return isUsed;
// }
function validateUsedMobile(mobile,asy,obj){
	if(asy!=false){
		asy = true;
	}
	var isUsed = true;
	$.ajax({
		url : verifymobile_url,
		data : {
			'mobile' : mobile
		},
		dataType : 'json',
		async : asy,
		success : function(data) {
			if(asy){
				if (data.code == '1') {
					divphone.innerHTML='<font class="tips_true"></font>';
				}else{
					divphone.innerHTML='<font class="tips_false">该手机号已注册</font>';
				}
			}else{
				if (data.code == '1') {
					isUsed=true;
				} else {
					isUsed=false;
				}
			}
		}
	});
	return isUsed;
}
function validateInviter(invite_code,asy,obj){
	if(asy!=false){
		asy = true;
	}
	var isUsed = true;
	if(invite_code==''){
		return true;
	}
	$.ajax({
		url : verifyinviter_url,
		data : {
			'invite' : invite_code
		},
		dataType : 'json',
		async : asy,
		success : function(data) {
			if(asy){
				if (data.code == '1') {
					divinvite.innerHTML='<font class="tips_true"></font>';
				}else{
					divinvite.innerHTML='<font class="tips_false">该邀请人不存在</font>';
				}
			}else{
				if (data.code == '1') {
					isUsed=true;
				} else {
					isUsed=false;
				}
			}
		}
	});
	return isUsed;
}
// function is_email(obj, checkUsed) {
// 	if (obj.val() == '') {
// 		divmail.innerHTML='<font class="tips_false">请输入邮箱地址</font>';
// 		obj.css("border-color","#f01e32");
// 		return true;
// 	} else if (!validateEmail(obj.val())) {
// 		divmail.innerHTML='<font class="tips_false">邮箱格式不正确</font>';
// 		obj.css("border-color","#f01e32");
// 		return true;
// 	}else {
// 		if(checkUsed) {
// 			validateUsedEmail(obj.val(),true,obj);
// 		}
// 		return false;
// 	}
// }

function is_ma(obj) {
	if (obj.val() == '' || obj.val() == '验证码') {
		divcode.innerHTML='<font class="tips_false">请输入手机验证码</font>';
		obj.css("border-color","#f01e32");
		return true;
	} else if (!validatetelcode(obj.val())) {
		divcode.innerHTML='<font class="tips_false">手机验证码不正确</font>';
		obj.css("border-color","#f01e32");
		return true;
	} else {
		divcode.innerHTML='<font class="tips_true"></font>';
		return false;
	}
}

function is_tel(obj, checkUsed) {
	if (obj.val() == '') {
		obj.css("border-color","#f01e32");
		divphone.innerHTML='<font class="tips_false">请输入手机号</font>';
		return true;
	} else if (!validatePhone(obj.val())) {
		obj.css("border-color","#f01e32");
		divphone.innerHTML='<font class="tips_false">手机号格式不正确</font>';
		return true;
	} else {
		if(checkUsed) {
			validateUsedMobile(obj.val(),true,obj);
		}
		return false;
	}

}

// function is_net_code(obj) {
// 	if (obj.val() == '') {
// 		divyzm.innerHTML='<font class="tips_false">请输入网页验证码</font>';
// 		obj.css("border-color","#f01e32");
// 		return true;
// 	} else if (!validatenetcode(obj.val())) {
// 		divyzm.innerHTML='<font class="tips_false">验证码格式不正确</font>';
// 		obj.css("border-color","#f01e32");
// 		return true;
// 	} else {
// 		divyzm.innerHTML='<font class="tips_true"></font>';
// 		return false;
// 	}

// }

// function is_net_code1(obj) {
// 	if (obj.val() == '') {
// 		divyzm.innerHTML='<font class="tips_false">请输入网页验证码</font>';
// 		return true;
// 	} else {
// 		return false;
// 	}

// }

function is_set_pd(obj) {
	if (obj.val() == '') {
		divpd.innerHTML='<font class="tips_false">请设置登录密码</font>';
		obj.css("border-color","#f01e32");
		return true;
	} else if (!validatePassport(obj.val())) {
		divpd.innerHTML='<font class="tips_false">密码格式不正确</font>';
		obj.css("border-color","#f01e32");
		return true;
	} else {
		divpd.innerHTML='<font class="tips_true"></font>';
		return false;
	}
}

// function is_sure_pd(obj) {
// 	if (obj.val() == '') {
// 		divspd.innerHTML='<font class="tips_false">请再次输入密码</font>';
// 		obj.css("border-color","#f01e32");
// 		return true;
// 	} else if (!is_panduan(obj.val())) {
// 		divspd.innerHTML='<font class="tips_false">两次密码输入不相同</font>';
// 		obj.css("border-color","#f01e32");
// 		return true;
// 	} else if (!validatePassport(obj.val())) {
// 		divspd.innerHTML='<font class="tips_false">密码格式不正确</font>';
// 		obj.css("border-color","#f01e32");
// 		return true;
// 	} else {
// 		divspd.innerHTML='<font class="tips_true"></font>';
// 		return false;
// 	}
// }

function is_panduan(str) {
	if (str == $("input[name='password1']").val()) {
			return true;
		} else {
			return false;
		}
}

function is_panduan2(str) {
	if (str.length >= 6 && str.length <= 16) {
		return true;
	} else {
		return false;
	}
}

function is_invite(obj, checkUsed) {
	if (obj.val() == '') {
		divinvite.innerHTML='<font class="tips_true"></font>';
		return false;
	} else {
		if(checkUsed) {
			validateInviter(obj.val(),true,obj);
		}
		return false;
	}

}
var usercheck=false;
var telcode=false;
$(document).ready(function() {
	// $("input[name='username']").blur(function() {
	// 	is_username($(this),true);
	// });

	// $("input[name='email']").blur(function() {
	// 	is_email($(this),true);
	// });


	$("input[name='mobile']").blur(function() {
		is_tel($(this),true);
	});

	// $("input[name='x_yanzhengma']").blur(function() {
	// 	is_net_code1($(this));
	// });

	$("input[name='code']").blur(function() {
		is_ma($(this));
	});

	$("input[name='password1']").blur(function() {
		is_set_pd($(this));
	});

	// $("input[name='password2']").blur(function() {
	// 	is_sure_pd($(this));
	// });

	$("input[name='invite']").blur(function() {
		is_invite($(this),true);
	});
	// 模拟原生的checkbox
//	$(".moni-checked").find("input").attr("checked","checked");
//	$(".g-checkbox,.g-lab-txt").click(function(){
//		if($(this).parent().find("input").attr("checked")!="checked"){
//			$(this).parent().find("input").attr("checked","checked");
//			$(this).parent().find(".g-checkbox").css("background-position","0 0");
//		}else{
//			$(this).parent().find("input").attr("checked",false);
//			$(this).parent().find(".g-checkbox").css("background-position","0 -18px")
//		}
//	})

	// 获得焦点后添加新的样式代码
	$("input[type=text],input[type=password]").focus(function(){
		$(this).css("border-color","#74b2ff");
	})

	// $(".imageCheckRefresh").click(function(){
	//       $.getJSON(coderefresh_url, function(json) {
	//           var new_cptch_key = json['key'];
	//           var new_cptch_image = json['image_url'];
	//           key = $("#id_hashkey");
	//           img = $("#id_checkImg");
	//           key.attr("value", new_cptch_key);
	//           img.attr("src", new_cptch_image);
	//       });
	//  });

	$("input[name='registSubmit']").click(function() {
		var flag = true;
		// if (is_username($("input[name='username']"), false)) {
		// 	flag = false;
		// }
		// if (is_email($("input[name='email']"), false)) {
		// 	flag = false;
		// }
		if (is_tel($("input[name='mobile']"), false)) {
			flag = false;
		}
		if (is_ma($("input[name='code']"))) {
			flag = false;
		}
		if (is_set_pd($("input[name='password1']"))) {
			flag = false;
		}
		// if (is_sure_pd($("input[name='password2']"))) {
		// 	flag = false;
		// }
		if (is_invite($("input[name='invite']"), false)) {
			flag = false;
		}
		if (flag) {
			if (document.getElementById("agreeChk").checked) {
				// if(validateUsedUsername($("input[name='username']").val(),false)){
				// 	usercheck = true;
				// }else{
				// 	alert("用户名已经被占用，请重新填写。");
				// 	return
				// }
				// if(validateUsedEmail($("input[name='email']").val(),false)){
				// 	usercheck = true;
				// }else{
				// 	alert("邮箱已经被占用，请重新填写。");
				// 	return
				// }
				if(validateUsedMobile($("input[name='mobile']").val(),false)){
					usercheck = true;
				}else{
					alert("手机号已经被占用，请重新填写。");
					return
				}
				if(validateInviter($("input[name='invite']").val(),false)){
					usercheck = true;
				}else{
					alert("邀请码无效，请不要填写或填写正确的邀请码。");
					return
				}
				$.ajax({
					url : register_url,
					data : {
						// 'username': $("input[name='username']").val(),
						'password': $("input[name='password1']").val(),
						'code' : $("input[name='code']").val(),
						'mobile' : $("input[name='mobile']").val(),
						// 'email': $("input[name='email']").val(),
						'invite': $("input[name='invite']").val(),
					},
					dataType : 'json',
					async:false,
					type:'POST',
					success : function(data) {
						if (data.code == '0') {
							window.location.href = index_url;
						}
						else {
							alert(data.msg);
						}
					},
					error : function() {
						alert("网络异常，请检查网络设置。");
						return false;
					}
				});
			}
			else{
				alert("请您仔细阅读并勾选注册协议，以完成注册");
			}
		}
	})
})

 function showBlock(){
     jQuery.blockUI({ message: "处理中，请稍候...",
                      css: {color:'yellow',border:'3px solid #aaa',
                      backgroundColor:'#000'},
                      overlayCSS: {backgroundColor:'#000',opacity:0.5 }});
}
