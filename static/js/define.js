$(document).ready(function(){
	$(".index_13_nav > a").mouseover(function(){
		var i = $(this).index();
		$("#index_12 > .index_15 > ul").eq(i).show().siblings("ul").hide();
		$("#index_12 > .index_15 > .icobox").show();
		$(this).css({"background":"#fff","color":"#ff8b52"}).siblings().css({"background":"#ff8b52","color":"#fff"});
	});
	
	$(".index_17_nav > a").mouseover(function(){
		var i = $(this).index();
		$(".index_18 > ul").eq(i).show().siblings().hide();
		$(".index_18 > .icobox").show();
		$(this).css({"background":"#fff","color":"#00d6b3"}).siblings("ul").css({"background":"#00d6b3","color":"#fff"});
	});
	
	$(".index_21_nav > a").mouseover(function(){
		var i = $(this).index();
		$(".index_22 > ul").eq(i).show().siblings().hide();
		$(".index_22 > .icobox").show();
		$(this).css({"background":"#fff","color":"#52c5ff"}).siblings("ul").css({"background":"#52c5ff","color":"#fff"});
	});
	
});
