function createGuide () {

  var guide_div = document.createElement('div');
  guide_div.className = 'guide-box';
  guide_div.innerHTML = '<div class="guide-box"><ul class="guide">'+
  '<li style="display: block; left: 600px; top: 66px;" class="guide__01 guide__item">'+
  '<img src="/static/images/guide-welfare.png" alt=""><a class="guide__btn01 guide__btn">'+
  '<img src="/static/images/guide-next-btn.png" alt=""></a>'+
  '<a style="margin-left: 250px; margin-top: 80px" class="guide__pass guide__btn">'+
  '<img src="/static/images/guide-pass.png" alt=""></a></li>'+

  '<li style="display: none; left: 694px; top: 100px;" class="guide__02 guide__item">'+
  '<img src="/static/images/guide-task.png" alt="">'+
  '<a class="guide__btn02 guide__btn">'+
  '<img style="margin-left: -100px;" src="/static/images/guide-next-btn.png" alt=""></a></li>'+

  '<li style="display: none; left: 794px; top: 100px;" class="guide__03 guide__item">'+
  '<img src="/static/images/guide-p2p.png" alt="">'+
  '<a class="guide__btn03 guide__btn">'+
  '<img style="margin-left: -200px;" src="/static/images/guide-next-btn.png" alt=""></a></li>'+

  '<li style="display: none; left: 700px; top: 100px;" class="guide__04 guide__item">'+
  '<img src="/static/images/guide-money.png" alt="">'+
  '<a class="guide__btn04 guide__btn">'+
  '<img style="margin-left: -200px;" src="/static/images/guide-next-btn.png" alt=""></a></li>'+

  '<li style="display: none; left: 0; top: 160px;" class="guide__05 guide__item next-hongbao">'+
  '<img src="/static/images/guide-lefticon.png" alt="">'+
  '<a class="guide__btn05 guide__btn">'+
  '<img style="margin-left: 400px;" src="/static/images/guide-next-btn.png" alt=""></a></li>'+

  '<li style="display: none; left: 260px; top: 26px;" class="guide__06 guide__item now-hongbao guide-end">'+
  '<img src="/static/images/guide-support.png" alt="">'+
  '<a class="guide__btn06 guide__btn">'+
  '<img style="margin-left: 200px;" src="/static/images/guide-know.png" alt=""></a></li>'+
  '</ul></div>';
  document.getElementsByTagName("body")[0].appendChild(guide_div);
  document.getElementsByTagName("body")[0].style.overflow='hidden';
  $('.guide__btn').click(function() {

  $(this).parent().next().css('display', 'block');
  $(this).parent().css('display', 'none');
  if ($(this).parent().hasClass('next-hongbao')) {
      window.scrollTo(0,900);
  }
  if ($(this).parent().hasClass('now-hongbao')) {
      window.scrollTo(0,0);
  }
  if ($(this).parent().hasClass('guide-end')) {
      document.getElementsByTagName("body")[0].removeChild(guide_div);
      // $(this).parent().parent().parent().css('display', 'none');
      document.getElementsByTagName("body")[0].style.overflow='auto';
  }
  });
  $('.guide__pass').click(function() {
  // $(this).parent().parent().parent().css('display', 'none');
  document.getElementsByTagName("body")[0].removeChild(guide_div);
  document.getElementsByTagName("body")[0].style.overflow='auto';
  });
}
