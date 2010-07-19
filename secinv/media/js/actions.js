
$(function() {

    $('select#machine-hostname, select#machine-ip, select#machine-domain, select[id$=-parameter]').change(function() {
        $(this).closest('form').submit();
    }).keyup(function() {
        $(this).closest('form').submit();
    }).keydown(function() {
        $(this).closest('form').submit();
    });

    $("select[id$='-parameter']").each(function(index) {
        var section = $(this).attr('id').split('-')[0];

        /*
        $('select#' + section + '-value').change(function() {
            $(this).closest('form').submit();
        }).keyup(function() {
            $(this).closest('form').submit();
        }).keydown(function() {
            $(this).closest('form').submit();
        });
        */


        if ($('select#' + section + '-parameter').val() == '' &&
            $('select#' + section + '-parameter').find('option').length == 1)
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
    var paramVal = $('select#' + section + '-parameter').val();

    if (paramVal == '')
        $('select#' + section + '-value').html('<option value="">*</option>\n');
    else {
        $.post(urls[section][1], { parameter: paramVal }, function(data) {

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

