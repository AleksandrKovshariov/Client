$(function () {
    "use strict";

    const progress_bar = $('.progress-bar');
    const status = $('#status');
    const btn_submit = $('#submit');

    $('#upload_form').ajaxForm({
        beforeSend: function() {
            status.empty();
            let percentVal = '0%';
            progress_bar.width(percentVal);
            progress_bar.html(percentVal);
            btn_submit.val("Loading...");
            btn_submit.prop('disabled', true);
        },
        uploadProgress: function(event, position, total, percentComplete) {
            let percentVal = percentComplete + '%';
            progress_bar.width(percentVal);
            progress_bar.html(percentVal);
        },
        complete: function(xhr) {
            status.html(xhr.responseText);
            btn_submit.val("Upload");
            btn_submit.prop('disabled', false);
        }
    });
});