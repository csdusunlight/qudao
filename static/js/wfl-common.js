;(function($,window,document,undefined) {

	$.fn.addTitle = function() {
		return this.each(function() {
			$(this).attr('title', $(this).text());
		})
	}

// 超出隐藏部分
$('.txtinline').each(function(index, el) {      //多行
    var overFlag = $(this).height()-$(this).parent().height();
    console.log($(this).height());
    console.log($(this).parent().height());
    if (overFlag > 0) {
        $(this).addTitle();
        $(this).parent().addClass('toolong');
    }
});
$('.oneline').each(function(index, el) {        //单行
    if ($(this).height() > 40) {
        $(this).addClass('one-line')
        $(this).addTitle();
    }
});
// 超出隐藏部分---end
})(jQuery,window,document)


var canclePopup = function(obj) {       //取消自定义弹窗
    $(obj).parent().parent().parent().removeClass('in');
}

