"use strict";
let checking_progress = true;
let ignore_count = 0;

function download_url() {
    console.log('download_url');
    $.ajax({
        url:'/download',
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
                $(':input[name=\'filename\']').val('');
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


function status() {
    console.log('status');
    if (!checking_progress) {
        if (ignore_count >= 10) {
            ignore_count = 0;
        } else {
            ignore_count += 1;
            return;
        }
    }
    console.log('network');
    $.ajax({
        url: '/status',
        type: 'GET',
        success: function(data) {
            data = JSON.parse(data);
            if (typeof data !== typeof {}){
                alert(data);
                return;
            }
            let progress = data.progress;
            let downloads = data.downloads;
            if (downloads.length === 0) {
                $('#dwnld-display *').remove();
                let p = document.createElement('p');
                $(p).text('No Downloads Available!').appendTo('#dwnld-display');
            }
            else {
                $('#dwnld-display *').remove();
                for (let i = 0; i < downloads.length; i++) {
                    let cloned = $('#samples #dwnld').clone();
                    cloned.find('#name').text(downloads[i]['name']);
                    cloned.find('#size').text(downloads[i]['size']);
                    cloned.find('#download').attr('href', downloads[i]['href']);
                    cloned.find('#multi-download').attr('href', 'split_download/'+downloads[i]['index']);
                    $('#dwnld-display').append(cloned);
                }
            }
            if (progress.length === 0) {
                checking_progress = false;
                $('#progress-display #progress').remove();
            }
            else {
                $('#progress-display #progress').remove();
                for (let i = 0; i < progress.length; i++) {
                    let cloned = $('#samples #progress').clone();
                    cloned.find('#name').text(progress[i]['name']);
                    cloned.find('#progress-view').attr('style', 'width: '+progress[i]['progress']+'%;');
                    $('#progress-display').append(cloned);
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
        url: '/progress',
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
                    cloned.find('#name').text(data[i]['name']);
                    cloned.find('#progress-view').attr('style', 'width: '+data[i]['progress']+'%;');
                    $('#progress-display').append(cloned);
                }
            }
        }
    });
}


if (page==='HOME') {
    setInterval(status, 1000);
} else if (page==='SETTINGS') {
alert("settings");
        $.ajax({
        url:'/settings_api',
        type:'get',
error:function (a,b,c) {
alert(a);
alert(b);
alert(c);
}
        success:function (data) {
            alert(data);
            data = JSON.parse(data);
            window.data = data;
            for (let key in data) {
                if (key === 'tokens') {
                    reloadTokens();
                }
                else {
                    if (typeof data[key] === typeof false) {
                        $('[name="'+key+'"]')[0].checked = data[key];
                    }
                    else {
                        $('[name="'+key+'"]').val(data[key]);
                    }
                }
            }
        }
    });

}

function save_settings () {
    let data = {};
    $('input[data-type="setting"]').each(function () {
        if ($(this).attr('type') === 'checkbox') {
            data[$(this).attr('name')] = $(this)[0].checked;
        }
        else if ($(this).attr('type') === 'number') {
            data[$(this).attr('name')] = parseInt($(this).val());
        } else {
            console.log(this);
            data[$(this).attr('name')] = $(this).val();
        }
    });
    data['tokens'] = JSON.stringify(window.data.tokens);
    console.log(data);
    $.ajax({
        url:'/settings_api',
        type:'post',
        data: data,
        success:function (data) {
            data = JSON.parse(data);
            if (data['status'] === 'success') {
                alert('Settings Saved');
            } else {
                alert(JSON.stringify(data));
            }
        }
    });

}

function deleteToken(e) {
    let id = parseInt($(e).attr('data-id'));
    let token = window.data['tokens'][id];
    if (confirm('Are you sure you want to delete this token?\n\n\''+token.token+'\'')) {
        window.data['tokens'].splice(id, 1);
        $(e).parents('li').slideUp(400, reloadTokens);
        // reloadTokens();
    }
}

function reloadTokens() {
    $('#tokens *').remove();
    for (var i = 0; i < window.data.tokens.length; i++) {
        let token = window.data.tokens[i];
        let clone = $('#templates #token-template').clone();
        clone.find('#token').text(token.token);
        clone.find('.w3-check')[0].checked = token.is_admin;
        clone.find('.w3-closebtn').attr('data-id', i);
        $('#tokens').append(clone);
    };
}

function addToken() {
    let token = $('[name="token"]').val();
    if (token.length === 0) {
        alert('Token can\'t be empity');
        return;
    }
    let is_admin = false;
    window.data.tokens.push({token, is_admin});
    reloadTokens()
    $('[name="token"]').val('');
}

function toggleTokenState (e) {
    let id = parseInt($(e).parents('#token-template').find('.w3-closebtn').attr('data-id'));
    window.data.tokens[id].is_admin = e.checked;
}
