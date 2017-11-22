var doc_id = "{{doc.id}}";
console.log(doc_id);
//分享复制部分
var btns = $('.copy-link')[0];
var clipboard = new Clipboard(btns);

clipboard.on('success', function(e) {
    console.log(e);
    $('.share-alert').addClass('m-show');
    window.setTimeout(function(){
        $('.share-alert').removeClass('m-show');
    }, 2000)
});

clipboard.on('error', function(e) {
    console.log(e);
});
//分享复制部分---end
$('.doc_del').click(function(){     //删除文档
    $(".popup.m-del-doc").addClass('in');
})
$("#confirm_delete").click(function(){
    var doc_id = "{{doc.id}}";
    $.ajax({            //删除文档
        url: "/restapi/docs/" + doc_id + "/",
        dataType: "json",
        type: 'delete',
        success: function(ret) {
            console.log('删除成功');
            $(".popup.m-del-doc").removeClass('in');
            window.location.href="/docs/list/"; 
            
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(jqXHR.responseText);
            console.log("数据错误");
        }
    });
})
//实例化编辑器
var um = UM.getEditor('myEditor', {
    toolbar:[
        'undo redo | bold italic underline strikethrough | forecolor backcolor | removeformat |',
        'insertorderedlist insertunorderedlist | selectall cleardoc | paragraph fontfamily fontsize' ,
        '| justifyleft justifycenter justifyright justifyjustify |',
        'link unlink | image ',
        '| horizontal'
    ]
});
if ($('.proj__title').val() == '') {
    $('.proj__title').val('无标题');
}
$('.proj__title').focus(function(){
    if ($(this).val() == '无标题') {
        $(this).val('');
    }
})
$('.proj__title').blur(function(){
    if ($(this).val() == '') {
        $(this).val('无标题');
    }
})

$('.proj__title').keyup(function(){
    var title = $('.proj__title').val();
    var content = UM.getEditor('myEditor').getContent();
    $.ajax({            //保存文档
        url: "/restapi/docs/" + doc_id + "/",
        dataType: "json",
        type: 'put',
        data: {
            'title': title, 
        },
        success: function(ret) {
            console.log('保存成功');
            $('.header__title').text(title);
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(jqXHR.responseText);
            console.log("数据错误");
        }
    });
})