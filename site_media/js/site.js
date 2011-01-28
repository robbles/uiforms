(function() {

$(document).ready(function() {

    $('.preview-link').click(function() {
        href = this.href + '?showNav=false&autoUpdate=true';
        newWindow = window.open(href, 'Preview', 'width=850,height=600')
        return false;
    }).text('Live Preview');

});

})();
