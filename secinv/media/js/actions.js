//var sections = ['apacheconfig', 'mysqlconfig', 'phpconfig'];


$(function() {

    $('select#machine-hostname, select#machine-ip, select#machine-domain, select#apacheconfig-value').change(function() {
        $(this).closest('form').submit();
    }).keyup(function() {
        $(this).closest('form').submit();
    }).keydown(function() {
        $(this).closest('form').submit();
    });

/*
    for (section_index in sections) {
        var section = sections[section_index];

        if ($('select#' + section + '-parameter').val() == '' && $('select#' + section + '-parameter').find('option').length == 1)
            doPopulate(section);

        $('select#' + section + '-parameter').change(function() {
            doChange(section);
        }).keyup(function() {
            doChange(section);
        }).keydown(function() {
            doChange(section);
        });
    }
*/

    $("select[id$='-parameter']").each(function(index) {
        var section = $(this).attr('id').split('-')[0];
        //$('#masthead').append($(this).attr('id').split('-')[0] + " " + urls[section][0] + " -- " + urls[section][1] + "\n");

        if ($('select#' + section + '-parameter').val() == '' && $('select#' + section + '-parameter').find('option').length == 1)
            doPopulate(section);

        $('select#' + section + '-parameter').change(function() {
            doChange(section);
        }).keyup(function() {
            doChange(section);
        }).keydown(function() {
            doChange(section);
        });

    });

});


function doPopulate(section) {
    $.getJSON(urls[section][0], function(data) {
        var foundSelected = false;

        $.each(data, function(key, value) {
            var selected = '';

            if (acParameter == data[key]) {
                selected = ' selected';
                foundSelected = true;
            }

            $('select#' + section + '-parameter').append("<option" + selected + ">" + value + "</option>\n");
        });

        if (foundSelected)
            doChange(section);
    });
}

function doChange(section) {
    //if ($('select#' + section + '-value').val() != '')
    //    return;

    //$('#masthead').append(section + "<br>\n");

    var paramVal = $('select#' + section + '-parameter').val();

    if (paramVal == '')
        $('select#' + section + '-value').html('<option value="">*</option>\n');
    else {
        $.post(urls[section][1], { parameter: paramVal }, function(data) {

            //$('#masthead').append("changing ... " + section + "<br>\n");

            var newOptions = '<option value="">*</option>\n';

            $.each(data, function(key, value) {
                var selected = '';
                if (acValue == value)
                    selected = ' selected';

                newOptions += "<option" + selected + ">" + value + "</option>\n";
            });

            $('select#' + section + '-value').html(newOptions); 
        });
    }
}

