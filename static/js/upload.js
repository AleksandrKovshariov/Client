$(function () {
    "use strict";

    const progress_bar = $('.progress-bar');
    const status = $('#status');

    $('#upload_form').ajaxForm({
        beforeSend: function() {
            status.empty();
            let percentVal = '0%';
            progress_bar.width(percentVal);
            progress_bar.html(percentVal);
        },
        uploadProgress: function(event, position, total, percentComplete) {
            let percentVal = percentComplete + '%';
            progress_bar.width(percentVal);
            progress_bar.html(percentVal);
        },
        complete: function(xhr) {
            status.html(xhr.responseText);
        }
    });
});