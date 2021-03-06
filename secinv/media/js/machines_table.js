var oCache = {
    iCacheLower: -1
};

function fnSetKey(aoData, sKey, mValue) {
    for (var i = 0, iLen = aoData.length; i < iLen; i++) {
        if (aoData[i].name == sKey) {
            aoData[i].value = mValue;
        }
    }
}

function fnGetKey(aoData, sKey) {
    for (var i = 0, iLen = aoData.length; i < iLen; i++) {
        if (aoData[i].name == sKey) {
            return aoData[i].value;
        }
    }
    return null;
}

function fnDataTablesPipeline(sSource, aoData, fnCallback) {
    var iPipe = 50, /* Ajust the pipe size */
        bNeedServer = false,
        sEcho = fnGetKey(aoData, "sEcho");
        iRequestStart = fnGetKey(aoData, "iDisplayStart");
        iRequestLength = fnGetKey(aoData, "iDisplayLength");
        iRequestEnd = iRequestStart + iRequestLength;
    oCache.iDisplayStart = iRequestStart;

    /* outside pipeline? */
    if (oCache.iCacheLower < 0 ||
        iRequestStart < oCache.iCacheLower ||
        iRequestEnd > oCache.iCacheUpper) {
        bNeedServer = true;
    }

    /* sorting etc changed? */
    if (oCache.lastRequest && !bNeedServer) {
        for (var i = 0, iLen = aoData.length; i < iLen; i++) {
            if (aoData[i].name != "iDisplayStart" &&
                aoData[i].name != "iDisplayLength" &&
                aoData[i].name != "sEcho") {
                if (aoData[i].value != oCache.lastRequest[i].value) {
                    bNeedServer = true;
                    break;
                }
            }
        }
    }

    /* Store the request for checking next time around */
    oCache.lastRequest = aoData.slice();

    if (bNeedServer) {
        if (iRequestStart < oCache.iCacheLower) {
            iRequestStart = iRequestStart - (iRequestLength * (iPipe - 1));

            if (iRequestStart < 0) {
                iRequestStart = 0;
            }
        }

        oCache.iCacheLower = iRequestStart;
        oCache.iCacheUpper = iRequestStart + (iRequestLength * iPipe);
        oCache.iDisplayLength = fnGetKey(aoData, "iDisplayLength");
        fnSetKey(aoData, "iDisplayStart", iRequestStart);
        fnSetKey(aoData, "iDisplayLength", iRequestLength * iPipe);

        $.getJSON(sSource, aoData, function (json) {
            /* Callback processing */
            oCache.lastJson = jQuery.extend(true, {}, json);

            if (oCache.iCacheLower != oCache.iDisplayStart) {
                json.aaData.splice(0, oCache.iDisplayStart - oCache.iCacheLower);
            }
            json.aaData.splice(oCache.iDisplayLength, json.aaData.length);

            fnCallback(json);
        });
    } else {
        json = jQuery.extend(true, {}, oCache.lastJson);
        json.sEcho = sEcho; /* Update the echo for each response */
        json.aaData.splice(0, iRequestStart-oCache.iCacheLower);
        json.aaData.splice(iRequestLength, json.aaData.length);
        fnCallback(json);
        return;
    }
}

$(document).ready(function() {
    $('#machines-index').dataTable({
        "bProcessing": true,
        "bServerSide": true,
        "sAjaxSource": $('#machines-index').attr('data-src'),
        "fnServerData": fnDataTablesPipeline,
        "aoColumns": [
            /* ID */
            {'bSearchable': false, 'bVisible': false},
            /* IP address */
            null,
            /* Hostname */
            null,
            /* External IP */
            null,
            /* httpd */
            null,
            /* mysqld */
            null,
            /* openvpn */
            null,
            /* NFS */
            null,
            /* Added */
            null,
            /* Scanned */
            null
        ]
    });
});
