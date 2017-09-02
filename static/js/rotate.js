var bRotate = false;
function rnd(n, m){
    return Math.floor(Math.random()*(m-n+1)+n)
}
var rotateFn = function (flag, angles, txt){
	$('#rotate').stopRotate();
	$('#rotate').rotate({
		angle:0,
		animateTo:angles+1800,
		duration:8000,
		callback:function (){
			if(flag){
				$(".popup1 font").text(txt);
				$(".popup1").css("display","block");
			}
			else{
				$(".popup6").css("display","block");
			}
			bRotate = false;
		}
	})
};
function lottery(item){
	var angle = rnd(3,57)
	switch (item) {
		case 2:
		angle += 30;
			rotateFn(1, angle, '10积分');
			break;
		case 4:
			angle += 90;
			rotateFn(1, angle, '0.8元现金');
			break;
		case 3:
			angle += 150;
			rotateFn(1, angle, '50积分');
			break;
		case 5:
			angle += -150;
			rotateFn(1, angle, '2元现金');
			break;
		case 1:
			angle += -90;
			rotateFn(0, angle, '谢谢参与');
			break;
		case 6:
			angle += -30;
			rotateFn(1, angle, 'iPhone');
			break;
	}
}
$(function (){
	var rotateTimeOut = function (){
        $('#rotate').rotate({
            angle:0,
            animateTo:2160,
            duration:8000,
            callback:function (){

            }
        });
    };
    var ajaxFunc = function(){
    	$.ajax({
			url: get_lottery_url,
			dataType:"json",
			type:"post",
			success:function(ret){
				if(ret.code==-1){
					alert("请先登录！")
					window.location.href = ret.url;
				}
				else if(ret.code==0){
					var itemid = ret.itemid
					itemid = parseInt(itemid)
					lottery(itemid);
				}
				else if(ret.code==-2){
					$(".popup7").css("display","block");
					bRotate = false;
				}
				else{
					alert("参数错误，请联系电话客服！");
					bRotate = false;
				}
			},
			error:function(){
				alert('网络超时，请检查您的网络设置！');
				bRotate = false;
			}
        });
    };
    $('.pointer').click(function (){
    	if (bRotate){
    		return;
    	}
    	else {
    		bRotate = true;
    		$(".popup4").css("display","block");
    	}
    });
    $('.confirm_lottery').click(function(){
    	bRotate = true;
    	ajaxFunc();
    });
    $('.btn_x').click(function(){
    	$(this).parent().parent().hide();
    	bRotate = false;
    });
    $('.btn_cont button').click(function(){
    	$(this).parent().parent().parent().parent().hide();
    });
});
