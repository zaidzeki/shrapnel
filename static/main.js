"use strict";
let checking_progress = true;
let last_loaded = -1;

function download_url() {
    console.log('download_url');
    $.ajax({
        url:'download/',
        type:'post',
        data:{
            'url':$('[name=\'url\']').val(),
            'filename':$('[name=\'filename\']').val()
        },
        success:function (data) {
            data = JSON.parse(data);
            if (data['status'] === 'success') {
                alert();
                $(':input[name=\'url\']').val('');
                if (!checking_progress) {
                    checking_progress = true;
                }
            }
            else {
                alert(JSON.stringify(data));
            }
        }
    });
}

function load_dwnld() {
    console.log('load_download');
    $.ajax({
        url: 'downloads/',
        type: 'GET',
        data:{
            start:0
        },
        success: function(data) {
            data = JSON.parse(data);
            if (typeof data !== typeof []){
                alert(data);
                return;
            }
            if (data.length === 0) {
                let p = document.createElement('p');
                $(p).text('No Downloads Available!').attr('#dwnld').appendTo('#dwnld-display');
            }
            else {
                $('#dwnld-display #dwnld').remove();
                for (let i = 0; i < data.length; i++) {
                    let cloned = $('#samples #dwnld').clone();
                    cloned.find('#url').text(data[i]['url']);
                    cloned.find('#download').attr('href', data[i]['href']);
                    cloned.find('#multi-download').attr('href', 'split_download/'+data[i]['index']);
                    $('#dwnld-display').append(cloned);
                }
            }
        }
    });
}

function load_progress() {
    console.log('load_progress');
    if (!checking_progress) {
        return;
    }
    $.ajax({
        url: 'progress/',
        type: 'GET',
        success: function(data) {
            data = JSON.parse(data);
            if (typeof data !== typeof []){
                alert(data);
                return;
            }
            if (data.length === 0) {
                checking_progress = false;
                $('#progress-display #progress').remove();
                load_dwnld();
            }
            else {
                if (!(last_loaded !== -1)) {
                    if (last_loaded !== data.length) {
                        load_dwnld();
                    }
                }
                last_loaded = data.length;
                $('#progress-display #progress').remove();
                for (let i = 0; i < data.length; i++) {
                    let cloned = $('#samples #progress').clone();
                    cloned.find('#progress_url').text(data[i]['url']);
                    cloned.find('#progress-view').attr('style', 'width: '+data[i]['progress']+'%;');
                    $('#progress-display').append(cloned);
                }
            }
        }
    });
}
setInterval(load_progress, 2500);
$(load_progress);
$(load_dwnld);
