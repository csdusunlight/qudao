var file_list = [];
//$(function() {
    var filechooser = document.getElementById("choose");
    //    用于压缩图片的canvas
    var canvas = document.createElement("canvas");
    var ctx = canvas.getContext('2d');
    //    瓦片canvas
    var tCanvas = document.createElement("canvas");
    var tctx = tCanvas.getContext("2d");
    var maxsize = 80 * 1024;
    $("#upload").on("click", function() {
        if(file_list.length >= 6) {
            alert("最多只可上传6张图片");
            return;
        }
        filechooser.click();
    })
    //    .on("touchstart", function() {
    //      $(this).addClass("touch")
    //    })
    //    .on("touchend", function() {
    //      $(this).removeClass("touch")
    //    });
    filechooser.onchange = function() {
        if(!this.files.length) return;
        var files = Array.prototype.slice.call(this.files);
        
        if(files.length + file_list.length > 6) {
            alert("最多只可上传6张图片");
            return;
        }
        files.forEach(function(file, i) {
            if(!/\/(?:jpeg|png|gif)/i.test(file.type)) return;
            var reader = new FileReader();
            var li = document.createElement("li");
            //          获取图片大小
            var size = file.size / 1024 > 1024 ? (~~(10 * file.size / 1024 / 1024)) / 10 + "MB" : ~~(file.size / 1024) + "KB";
            $(".img-list").append($(li));
            reader.onload = function() {
                var result = this.result;
                var img = new Image();
                img.src = result;
                $(li).css("background-image", "url(" + result + ")");
                //如果图片大小小于100kb，则直接上传
                if(result.length <= maxsize) {
                    img = null;
                    process(result, file.name, file.type);
                    return;
                }
                //      图片加载完毕之后进行压缩，然后上传
                if(img.complete) {
                    callback();
                } else {
                    img.onload = callback;
                }

                function callback() {
                    var data = compress(img);
                    process(data, file.name, file.type);
                    img = null;
                }
            };
            reader.readAsDataURL(file);
        })
    };
    //    使用canvas对大图片进行压缩
    function compress(img) {
        var initSize = img.src.length;
        var width = img.width;
        var height = img.height;
        //如果图片大于四百万像素，计算压缩比并将大小压至40万以下
        var ratio;
        if((ratio = width * height / 400000) > 1) {
            ratio = Math.sqrt(ratio);
            width /= ratio;
            height /= ratio;
        } else {
            ratio = 1;
        }
        console.log("ratio:" + ratio);
        canvas.width = width;
        canvas.height = height;
        //        铺底色
        ctx.fillStyle = "#fff";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        //如果图片像素大于100万则使用瓦片绘制
        var count;
        if((count = width * height / 1000000) > 1) {
            count = ~~(Math.sqrt(count) + 1); //计算要分成多少块瓦片
            //            计算每块瓦片的宽和高
            var nw = ~~(width / count);
            var nh = ~~(height / count);
            tCanvas.width = nw;
            tCanvas.height = nh;
            for(var i = 0; i < count; i++) {
                for(var j = 0; j < count; j++) {
                    tctx.drawImage(img, i * nw * ratio, j * nh * ratio, nw * ratio, nh * ratio, 0, 0, nw, nh);
                    ctx.drawImage(tCanvas, i * nw, j * nh, nw, nh);
                }
            }
        } else {
            ctx.drawImage(img, 0, 0, width, height);
        }
        //进行最小压缩
        var ndata = canvas.toDataURL('image/jpeg', 0.5);
//      console.log('压缩前：' + initSize);
//      console.log('压缩后：' + ndata.length);
//      console.log('压缩率：' + ~~(100 * (initSize - ndata.length) / initSize) + "%");
        tCanvas.width = tCanvas.height = canvas.width = canvas.height = 0;
        return ndata;
    }
    //    图片上传，将base64的图片转成二进制对象，塞进formdata上传
    function process(basestr, name, type, $li) {
        var text = window.atob(basestr.split(",")[1]);
        var buffer = new Uint8Array(text.length);
        for(var i = 0; i < text.length; i++) {
            buffer[i] = text.charCodeAt(i);
        }
        var blob = getBlob([buffer], type);
        file_list.push({
            name: name,
            blob: blob
        });
    }

    function submit() {
        var xhr = new XMLHttpRequest();
        var formdata = getFormData();
        var csrfmiddlewaretoken = document.getElementsByName("csrfmiddlewaretoken")[0].value;
        var telnum = $('input#telnum').val();
        var remark = $('input#remark').val();
        if(file_list.length == 0) {
            alert("请上传任务完成截图");
            return;
        }
        for(i in file_list) {
            formdata.append(file_list[i].name, file_list[i].blob);
        }
        formdata.append('id', id);
        formdata.append('telnum', telnum);
        formdata.append('remark', remark);
        formdata.append('csrfmiddlewaretoken', csrfmiddlewaretoken);
        xhr.open('post', '/expsubmit/task/');
        xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
        maskIn();
        xhr.onreadystatechange = function() {
            $(".img-mask").css("display", "none");
            if(xhr.readyState == 4 && xhr.status == 200) {
                var ret = JSON.parse(xhr.responseText);
                if(ret.code == 0) {
                    $(".img-mask").css("display", "none");
                    alert("请先登录！")
                    window.location.href = ret.url;
                    return;
                } else if(ret.code == 1) {
                    $("#hint").text("任务完成，请耐心等待工作人员审核!")
                    popupIn();
                } else {
                    $("#hint").text(ret.msg)
                    popupIn()
                }
            }
        };

        xhr.send(formdata);
    }
    /**
     * 获取blob对象的兼容性写法
     * @param buffer
     * @param format
     * @returns {*}
     */
    function getBlob(buffer, format) {
        try {
            return new Blob(buffer, {
                type: format
            });
        } catch(e) {
            var bb = new(window.BlobBuilder || window.WebKitBlobBuilder || window.MSBlobBuilder);
            buffer.forEach(function(buf) {
                bb.append(buf);
            });
            return bb.getBlob(format);
        }
    }
    /**
     * 获取formdata
     */
    function getFormData() {
        var isNeedShim = ~navigator.userAgent.indexOf('Android') &&
            ~navigator.vendor.indexOf('Google') &&
            !~navigator.userAgent.indexOf('Chrome') &&
            navigator.userAgent.match(/AppleWebKit\/(\d+)/).pop() <= 534;
        return isNeedShim ? new FormDataShim() : new FormData()
    }
    /**
     * formdata 补丁, 给不支持formdata上传blob的android机打补丁
     * @constructor
     */
    function FormDataShim() {
        console.warn('using formdata shim');
        var o = this,
            parts = [],
            boundary = Array(21).join('-') + (+new Date() * (1e16 * Math.random())).toString(36),
            oldSend = XMLHttpRequest.prototype.send;
        this.append = function(name, value, filename) {
            parts.push('--' + boundary + '\r\nContent-Disposition: form-data; name="' + name + '"');
            if(value instanceof Blob) {
                parts.push('; filename="' + (filename || 'blob') + '"\r\nContent-Type: ' + value.type + '\r\n\r\n');
                parts.push(value);
            } else {
                parts.push('\r\n\r\n' + value);
            }
            parts.push('\r\n');
        };
        // Override XHR send()
        XMLHttpRequest.prototype.send = function(val) {
            var fr,
                data,
                oXHR = this;
            if(val === o) {
                // Append the final boundary string
                parts.push('--' + boundary + '--\r\n');
                // Create the blob
                data = getBlob(parts);
                // Set up and read the blob into an array to be sent
                fr = new FileReader();
                fr.onload = function() {
                    oldSend.call(oXHR, fr.result);
                };
                fr.onerror = function(err) {
                    throw err;
                };
                fr.readAsArrayBuffer(data);
                // Set the multipart content type and boudary
                this.setRequestHeader('Content-Type', 'multipart/form-data; boundary=' + boundary);
                XMLHttpRequest.prototype.send = oldSend;
            } else {
                oldSend.call(this, val);
            }
        };
    }
//})
// 清除图片数据
function clearBtn() {
    $(".img-list").empty();
    file_list = [];
    console.log(file_list.length);
}