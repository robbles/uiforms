(function() {

$(document).ready(function() {

    console.log('preview refreshing enabled');
    var refresh_interval = 1000;

    var id = $('#uiform-id').attr('value');
    var status_url = $('#uiform-url').attr('value');
    var last_updated = parseInt($('#uiform-last-updated').attr('value'));

    if(typeof id == 'undefined' ||
       typeof status_url == 'undefined') {
        console.error("No UIForm metadata found, can't refresh");
        return;
    }

    setInterval(function() {
        
        // Load metadata from server as JSON
        $.getJSON(status_url, function(status, result) {
            // Check if UIForm has been updated
            if(status.last_updated != last_updated) {
                last_updated = status.last_updated;

                // Reload the form element with AJAX
                var form_id = '#preview-form-' + id;
                var remote_form = status.url + ' ' + form_id + '>*';
                $(form_id).load(remote_form);
            }
        });

    }, refresh_interval);

});

})();
