function show(obj, msg) {
	obj.addClass('error_input');
	obj.parent().find('.error_info').css('display', 'inline').css('color', 'red');
	obj.parent().find('.error_info').html('<i></i>' + msg);
};

function hidden(obj) {
	obj.removeClass('error_input');
	obj.parent().find('.error_info').html('');
};

function showPop(obg) {
	$(obg).css('display', 'block');
	$(':input',$(obg)).removeClass('error_input');
	$(':input',$(obg)).parent().find('.error_info').html('');
};

function hiddenPop(obg) {
	$(obg).css('display', 'none');
};
