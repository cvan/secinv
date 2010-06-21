$(function(){

    $('.tabs').tabs();

    $('select#machine-hostname, select#machine-ip, select#machine-domain').selectmenu({style:'dropdown', maxHeight: 200});
    //$('select#ac-filter-directives, select#ac-filter-directives-values').selectmenu({style:'dropdown'});

});
