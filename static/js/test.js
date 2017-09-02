alert("ddd");
$(function(){
	
	now = new Date(),hour = now.getHours();
	alert("ddd");
	if(hour < 6){$("#hello").text("凌晨好！");} 
	else if (hour < 9){$("#hello").text("早上好！");} 
	else if (hour < 12){$("#hello").text("上午好！");} 
	else if (hour < 14){$("#hello").text("中午好！");} 
	else if (hour < 17){$("#hello").text("下午好！");} 
	else if (hour < 19){$("#hello").text("傍晚好！");} 
	else if (hour < 22){$("#hello").text("晚上好！");} 
	else {$("#hello").text("夜里好！");}
	
	$(.Sign-on).click(function(){
		alert("dsf");
		$(this).addClass("off").removeClass("on");
	});
    (function copyInit(textId,buttonId) {
        ZeroClipboard.setMoviePath( "{% static 'swf/ZeroClipboard.swf' %}" );
        var clip = new ZeroClipboard.Client(); // 新建一个对象
        clip.setHandCursor( true ); // 设置鼠标为手型
        clip.setText($('#'+textId).val());
        clip.addEventListener('complete', function(){
            alert('复制成功！');
        });
        clip.glue(buttonId); // 和上一句位置不可调换
        $('#'+textId).change(function(){clip.setText($('#'+textId).val())});
    })('url-content','copy');
});