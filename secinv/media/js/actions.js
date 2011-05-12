var selectedSection = '';

$(function() {

    $('aside#sidebar select[id^=machine-], aside#sidebar select[id$=-value]').change(function() {
        $(this).closest('form').submit();
    }).keyup(function() {
        $(this).closest('form').submit();
    }).keydown(function() {
        $(this).closest('form').submit();
    });

    // Get section name of `selected` `option`'s parent `select` field.
    if ($('select[id$=-parameter] option[selected]').length) {
        selectedSection = $('select[id$=-parameter] option[selected]').parent().attr('id').split('-')[0];
    }

    $("select[id$='-parameter']").each(function(index) {
        var section = $(this).attr('id').split('-')[0];

        if ($('select#' + section + '-parameter').val() == '' &&
            $('select#' + section + '-parameter').find('option').length == 1) {
            doPopulate(section);
        }

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
    $.getJSON(filterURLs[section][0], function(data) {
        var foundSelected = false;

        $.each(data, function(key, value) {
            var selected = '';

            if (confParameter == data[key]) {
                selected = ' selected';
                foundSelected = true;
            }

            $('select#' + section + '-parameter').append("<option" + selected + ">" + value + "</option>\n");
        });

        // Remove currently selected option.
        if ($('select#' + section + '-parameter option[selected]:first-child').length) {
            $('select#' + section + '-parameter option:first-child').remove();
            $('select#' + section + '-parameter').prepend('<option value="">*</option>\n');
        }

        if (foundSelected)
            doChange(section);
    });
}

function doChange(section) {
    var paramVal = $('select#' + section + '-parameter').val();

    $("select[id$='-parameter']:not(#" + section + "-parameter").val('');

    // Clear currently selected fields.
    if (typeof selectedSection !== 'undefined' && section != selectedSection) {
        $('select#' + selectedSection + '-parameter, select#' + selectedSection + '-value').val('');
    }

    if (paramVal == '') {
        $('select#' + section + '-value').html('<option value="">*</option>\n');
    } else {
        $.post(filterURLs[section][1], { parameter: paramVal }, function(data) {

            var newOptions = '<option value="">*</option>\n';

            $.each(data, function(key, value) {
                var selected = '';
                if (confValue == value)
                    selected = ' selected';

                newOptions += "<option" + selected + ">" + value + "</option>\n";
            });

            $('select#' + section + '-value').html(newOptions);
        });
    }
}
