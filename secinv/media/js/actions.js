$(function(){

    //$('.ui-selectmenu-menu li a').attr('href', 'blah');

    $('select#machine-hostname, select#machine-ip, select#machine-domain, select#ac-filter-directives-values').change(function(){
        $(this).closest('form').submit();
    }).keyup(function(){
        $(this).closest('form').submit();
    }).keydown(function(){
        $(this).closest('form').submit();
    });

    var selected = $('select#ac-filter-directives').val();
    var numChildren = $('select#ac-filter-directives').find('option').length;

    if (selected == '' && numChildren == 1)
        doPopulate();

    $('select#ac-filter-directives').change(function(){
        doChange();
    }).keyup(function(){
        doChange();
    }).keydown(function(){
        doChange();
    });

/*
    $('select#ac-filter-directives').focus(function(){
        //alert('focused!');
        //doPopulate();
        //var options = $('select#ac-filter-directives').children('option').html();

        var selected = $('select#ac-filter-directives').val();
        var numChildren = $('select#ac-filter-directives').find('option').length;

        if (selected == '' && numChildren == 1)
            doPopulate();
    }).change(function(){
        doChange();
    }).keyup(function(){
        doChange();
    }).keydown(function(){
        doChange();
    });
*/

});


function doPopulate()
{
    $.getJSON(urlAllDirs, function(data) {
        var newHTML = "";

        $.each(data, function(key, value) {

            $('select#ac-filter-directives').append("<option>" + data[key] + "</option>\n");

            //newHTML += "key: " + data[key] + "<br>\n";

            /*
            $.each(data[key][1], function(k, v) {
                newHTML += "&nbsp;&nbsp; - " + v + "<br>\n";
            });
            */
            //newHTML += key + " - " + value;

        });
        //$('select#ac-filter-directives').selectmenu({style:'dropdown'});
    });
}

function doChange()
{
    var dirVal = $('select#ac-filter-directives').val();

    if (dirVal == '')
        $('select#ac-filter-directives-values').html('<option value="">*</option>\n');
    else
    {
        $.post(urlDirs, { directive: dirVal }, function(data) {
            var newOptions = '<option value="">*</option>\n';
    
            $.each(data, function(key, value) {
                newOptions += "<option>" + value + "</option>\n";
            });
    
            $('select#ac-filter-directives-values').html(newOptions);

            //$('select#ac-filter-directives-values').selectmenu({style:'dropdown'});

            //$('select#ac-filter-directives-values').focus();
        });
    }
}
