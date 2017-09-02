;(function($,window,document,undefined) {
//  绑定JQ的点击事件
    $.PopupClose = function (Id) {
        $('#'+Id+' .popup__close-btn').on('click', function(){
            var Id = $(this).parent().parent().parent().attr('id');     // 父窗ID
            $("#"+Id).removeClass('in');        // 向上滑动渐变退出
            window.setTimeout(function(){
                $("#"+Id).remove();
            },500);
        });
    }

    $.PopupClick = function (Id) {  // 关闭弹窗，业务处理时，弹窗关闭处
        // 向上滑动渐变退出
        $("#"+Id).removeClass('in');
        // 删除HTML实体
        window.setTimeout(function(){
            $("#"+Id).remove();
        },400);
    }

    $.confirm = function (Data) {       //确认提示框
        // 设置默认值
        var Data       = arguments[0]    ? arguments[0]    : '{}';
        var Id         = Data.Id         ? Data.Id         : 'popup_confirm';   //唯一ID值
        var Width      = Data.Width      ? Data.Width      : '600';     //弹窗宽度
        var Title      = Data.Title      ? Data.Title      : '标题';      //弹窗标题
        var Content    = Data.Content    ? Data.Content    : '内容文字';        //弹窗内容
        var NeedCancle   = Data.NeedCancle   ? Data.NeedCancle   : false;        //是否需要取消按钮
        var Cancle     = Data.Cancle     ? Data.Cancle     : '取消';      //取消按钮名称
        var Confirm    = Data.Confirm    ? Data.Confirm    : '确认';      //确认按钮名称
        var CancleFunc    = Data.CancleFunc    ? Data.CancleFunc    : '';       //取消回调函数
        var ConfirmFunc    = Data.ConfirmFunc    ? Data.ConfirmFunc    : '';        //确认回调函数

        var html = '';      // 开始组合弹窗HTML结构
        html +='<div id="'+Id+'" class="popup"><div class="popup__content" style="width: '+Width+'px;">';
        html +='<div class="popup__top"><h2 class="popup__title">'+Title+'</h2><button type="button" class="popup__close popup__close-btn">×</button></div>';
        html +='<div class="popup__detail">'+Content+'</div>';
        html +='<div class="popup__btnbox">';
        if(NeedCancle === true){
            html +='<a class="btn m-green m-popup popup-cancle popup__close-btn m-right">'+Cancle+'</a>';
        }
        html +='<a class="btn m-green m-popup popup-confirm popup__close-btn">'+Confirm+'</a>';
        html +='</div></div></div>';
        $(document.body).append(html);
        window.setTimeout(function(){       // 向下滑动渐现
            $("#"+Id).addClass('in');
        },50);
        $("#"+Id+" .popup-confirm").on('click', function(){     // 点击确认按钮回调
            if(ConfirmFunc != ''){
                eval(ConfirmFunc);
            }
        });
        $("#"+Id+" .popup-cancle").on('click', function(){      // 点击取消按钮回调
            if(CancleFunc != ''){
                eval(CancleFunc);
            }
        });
        $.PopupClose(Id);       // 开启监听关闭弹窗
    };

    $.warning = function (Data) {       //  警告提示框
        // 设置默认值
        var Data       = arguments[0]    ? arguments[0]    : '{}';
        var Id         = Data.Id         ? Data.Id         : 'popup_warming';
        var Title      = Data.Title      ? Data.Title      : '提示';
        var Content    = Data.Content    ? Data.Content    : '提示内容部分';
        var Width      = Data.Width      ? Data.Width      : '400';
        var Confirm    = Data.Confirm    ? Data.Confirm    : '知道啦';

        var html = '';
        html +='<div id="'+Id+'" class="popup"><div id="'+Id+'" class="popup__content" style="width: '+Width+'px;">';
        html +='<div class="popup__top"><h2 class="popup__title">'+Title+'</h2><button type="button" class="popup__close popup__close-btn">×</button></div>';
        html +='<div class="popup__detail">'+Content+'</div>';
        html +='<div class="popup__btnbox">';
        html +='<a class="btn m-green m-popup popup__close-btn">'+Confirm+'</a>';
        html +='</div></div></div>';
        $(document.body).append(html);
        window.setTimeout(function(){
            $("#"+Id).addClass('in');
        },50);
        $.PopupClose(Id);
    };
    $.prompt = function (Data) {        //文字提示框
        // 设置默认值
        var Data       = arguments[0]    ? arguments[0]    : '{}';
        var Id         = Data.Id         ? Data.Id         : 'popup_prompt';
        var Content    = Data.Content    ? Data.Content    : '提示内容部分';
        var Width      = Data.Width      ? Data.Width      : '600';
        var OutTime    = Data.OutTime    ? Data.OutTime    : 1500;

        if($("#"+Id).length!=0){    // 验证ID是否已经存在
            console.log('ID已存在，请修改！');
            return false;
        }
        var html = '';
        html +='<div id="'+Id+'" class="popup"><div id="'+Id+'" class="popup__content" style="width: '+Width+'px;">';
        html +='<div class="popup__top"><button type="button" class="popup__close popup__close-btn">×</button></div>';
        html +='<div class="popup__detail">'+Content+'</div>';
        html +='</div></div>';

        $(document.body).append(html);
        window.setTimeout(function(){
            $("#"+Id).addClass('in');
        },50);
        $.PopupClose(Id);
        window.setTimeout(function(){
            $('#'+Id+' .popup__close').trigger("click");
        },OutTime);
    };
//  弹窗部分---end

})(jQuery,window,document)
