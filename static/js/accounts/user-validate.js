
/**************************密码校验规则：数字，字母，非字母和数字，不是中文*********************/
function validatePassport(str){
			var re1 = /.*[0-9]+.*/;//数字
			var re2 = /.*[a-zA-Z]+.*/;//字母
			var re3 = /.*[^a-zA-Z0-9]+.*/;//非字母和数字
			var re4 = /.*[^\u4E00-\u9FA5]{0,}.*/;//不是中文
			//长度6-16
			if(!((str.length>=6)&&(str.length<=16))){
				return false;
			}
			/**
			必须是：字母和数字
			**/
			if((re1.test(str)&&re2.test(str)||
					re1.test(str)&&re3.test(str)||
					re2.test(str)&&re3.test(str)
					)&&re4.test(str)){
				return true;
			}
//			/**
//			必须是：数字和特殊符号
//			**/
//			if(re1.test(str)&&re3.test(str)&&re4.test(str)){
//				return true;
//			}
//			/**
//			必须是：字母和特殊符号
//			**/
//			if(re2.test(str)&&re3.test(str)&&re4.test(str)){
//				return true;
//			}
			return false;
	}


/******************** 用户名校验规则：注册的时候（头部尾部不能使空格，不能是中文，不能使全角，不能有星号，长度6-16)*****************/
function validateUserName(str){
	var reg = /^[A-Za-z0-9]+$/; //用户名
    var fullNumber = /^[0-9]+$/ //数字
   /***长度6-16*/
	if(!((str.length>=6)&&(str.length<=16))){
		return false;
	}
    
    if(!reg.test(str)){
		return false;
	}
    
    if(fullNumber.test(str)){
		return false;
	}
	return true;
}
/******************** QQ校验规则********************8*/
function validateQQ(str){
    var reQQ = /^[1-9]\d{4,9}$/; 
    if(!reQQ.test(str)){
        return false;
    }else{
        return true;
    }
}
/******************** QQName校验规则********************8*/
function validateQQname(str){
    if(!str){
        return false;
    }else{
        return true;
    }
}
/******************** intro个人简介校验规则********************8*/
function validateIntro(str){
    if(!((str.length>=10)&&(str.length<=200))){
        return false;
    }else{
        return true;
    }
}

/******************* 邮箱格式验证*********************8*/
function validateEmail(str){
	var re=/^([a-zA-Z0-9]+[_|\_|\.]?)*[a-zA-Z0-9]+@([a-zA-Z0-9]+[_|\_|\.]?)*[a-zA-Z0-9]+\.[a-zA-Z]{2,3}$/;
	if(re.test(str)){
		return true;
	}else{
		return false;
	}
}

/*******************手机格式验证*********************8*/
function validatePhone(str){   // 手机格式验证
	var re=/^1[1,2,3,4,6,5,7,8,9]\d{9}$/;//^1(3[0-9]|5[0-35-9]|8[0235-9])\\d{8} 
	if(re.test(str)){
		return true;
	}else{
		return false;
	}
}
/*******************网页验证码格式验证*********************8*/
function validatenetcode(str){
	/***长度4*/
	if(str.length>4||str.length<1){
		return false;
	}
	return true;						
}
/*******************手机验证码格式验证*********************8*/
function validatetelcode(str){
	/***长度4*/
	if(str.length>6||str.length<6){
		return false;
	}
	return true;						
}