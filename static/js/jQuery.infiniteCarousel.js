// JavaScript Document
(function () {
    $.fn.infiniteCarousel = function (options) {
	    // 设置参数
		options = $.extend({
					type:0,       // 0：左右 ，1：上下
				 	dire:0,    	  // 0:左上   1:右下
					float:0,      // 0：no    1: yes
				 	stopTime:5000,  // 默认显示时间
					moveTime:500,	// 默认移动时间
					auto:true
					},options); 
					
		
		// 添加空白元素
		function repeat(str, n) {
            return new Array( n + 1 ).join(str);
        }
		// 具体处理方法
		return this.each(function () {
			
			// 初始化参数
			var $wrapper = $("div[rel='wrapper']", this).css("overflow","hidden"),           // 显示层设为超出隐藏
				$slider = $wrapper.find("div[rel='slider']").width(999999).height(999999),   // 移动层宽高设为999999
				$items = $slider.find("div[rel='item']"),                                    // 元素集合
			    $single = $items.filter(":first"),                                             // 得到第一个元素
				
				singleWidth = $single.outerWidth(),                                            // 元素的宽度
				singleHeight = $single.outerHeight(),                                          // 元素的高度
				
				visibleWidth = Math.ceil($wrapper.innerWidth() / singleWidth),                 // 模向显示的个数
				visibleHeight = Math.ceil($wrapper.innerHeight() / singleHeight),              // 竖向显示的个数
				
				currentPage = 1,                                                               // 当前页数
				pages = 0,                                                                     // 总页数
				$currentPage = $("span[rel='cPage']",this),                            // 当前页数显示层
				$pages =  $("span[rel='tPage']",this);                                   // 总页数显示层
		 		 
			// alert($wrapper.scrollTop());
			if (options.float == 1) {
				$slider.width($wrapper.innerWidth());	 // 添加宽度
				visibleHeight = visibleWidth * visibleHeight;
				
			}
			
			// 一 如果有需要，用空的元素填充
			if (options.type == 0) {
				
				pages = Math.ceil($items.length / visibleWidth); //获得显示总页数
				 
				if ($items.length % visibleWidth != 0) { // 左右
					$slider.append(repeat('<div class="item" rel="item"/>', visibleWidth - ($items.length % visibleWidth)));
					$items = $slider.find('> div[rel="item"]');
				}
				
				// 2. 左右克隆出一个页面的内容。
				$items.filter(':first').before($items.slice(-visibleWidth).clone().addClass('cloned'));
				$items.filter(':last').after($items.slice(0, visibleWidth).clone().addClass('cloned'));
				$items = $slider.find('> div[rel="item"]');
				
				// 3 重置显示位置
				$wrapper.scrollLeft(singleWidth * visibleWidth);
				
				
			} else if (options.type == 1) {
				
				pages = Math.ceil($items.length / visibleHeight); //获得显示总页数
				
				if ($items.length % visibleHeight != 0) { //上下
					$slider.append(repeat('<div class="item" rel="item"/>', visibleHeight - ($items.length % visibleHeight)));
					$items = $slider.find('> div[rel="item"]');
				}
				
				// 2. 左右克隆出一个页面的内容。
				$items.filter(':first').before($items.slice(-visibleHeight).clone().addClass('cloned'));
				$items.filter(':last').after($items.slice(0, visibleHeight).clone().addClass('cloned'));
				$items = $slider.find('> div[rel="item"]');
				
				// 3 重置显示位置
				if(options.float == 1) {
					visibleHeight = (visibleHeight/visibleWidth);
					$wrapper.scrollTop(singleHeight * visibleHeight);
				}
				else
					$wrapper.scrollTop(singleHeight * visibleHeight);
			} 
			// 将总页数添加的显示层中。
			$pages.text(pages);   
			$currentPage.text(currentPage);
			 // 4. 翻页方法
            function gotoPage(page) { 
                var dir = page < currentPage ? -1 : 1,
                    n = Math.abs(currentPage - page),
                    left = singleWidth * dir * visibleWidth * n,
					top = singleHeight * dir * visibleHeight * n;
					
               
				if (options.type == 0) {
					$wrapper.filter(':not(:animated)').animate({
						scrollLeft : '+=' + left
					}, options.moveTime, function () {
						// if page == last page - then reset position
						if (page > pages) {
							$wrapper.scrollLeft(singleWidth * visibleWidth);
							page = 1;
						} else if (page == 0) {
							page = pages;
							$wrapper.scrollLeft(singleWidth * visibleWidth * pages);
						}
						
						currentPage = page;
						$currentPage.text(page);
					});
				}
				else if (options.type == 1) {
					$wrapper.filter(':not(:animated)').animate({
						scrollTop : '+=' + top
					}, options.moveTime, function () {
						
						// if page == last page - then reset position
						if (page > pages) {
							$wrapper.scrollTop(singleHeight * visibleHeight);
							page = 1;
						} else if (page == 0) {
							page = pages;
							$wrapper.scrollTop(singleHeight * visibleHeight * pages);
						}
						
						currentPage = page;
						$currentPage.text(page);
					});
				}  
				
            }
			
			// 按钮动作 
			$('div[rel="btn"]', this).click(function () {
			 
				// 向左，向上，
				if ($(this).attr('dire')==0 ) 
                	gotoPage(currentPage - 1); 
				// 向右，向下
				else if ($(this).attr('dire')==1 ) 
                	gotoPage(currentPage + 1);
                return false;
            });
			
			// 绑定翻页方法
			//$(this).bind('goto', function (event, page) {
            //    gotoPage(page);
            //});
            
            // 自动翻页方法
           // $(this).bind('next', function () {
           //     gotoPage(currentPage + 1);
           // });
			
			// 自动翻页
			
			 
			
			if($items.length > 0)
			{	
				$(this).mouseover(function () {
					options.auto = false;
				}).mouseout(function () {
					options.auto = true;
				});
				
				setInterval(function () {
					if (options.auto) {
						gotoPage(currentPage + 1);
					}
					}, options.stopTime); 
			}
			
			// function end
		});
	}
})(jQuery);