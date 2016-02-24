var http_request = false;


function makeRequest(url, type, para) {

    http_request = false;


    if (window.XMLHttpRequest) { // Mozilla, Safari,...
        http_request = new XMLHttpRequest();
        if (http_request.overrideMimeType) {
            http_request.overrideMimeType('text/xml');
            // Przeczytaj o tym wierszu poniżej
        }
    } else if (window.ActiveXObject) { // IE
        try {
            http_request = new ActiveXObject("Msxml2.XMLHTTP");
        } catch (e) {
            try {
                http_request = new ActiveXObject("Microsoft.XMLHTTP");
            } catch (e) { }
        }
    }

    if (!http_request) {
        addLog('Poddaję się :( Nie mogę stworzyć instancji obiektu XMLHTTP');
        return false;
    }

    http_request.onreadystatechange = function () { addLogContents(http_request); };
    http_request.open(type, url, true);
    http_request.setRequestHeader("Content-type", "application/x-www-form-urlencoded");


    var token = getCookie("csrftoken");
    var parameters = "csrfmiddlewaretoken=" + token + para;

    
    http_request.send(parameters);
}

function getCookie(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') c = c.substring(1);
        if (c.indexOf(name) == 0) return c.substring(name.length, c.length);
    }
    return "";
}

function addLogContents(http_request) {
    if (http_request.readyState == 4) {
        if (http_request.status == 200) {           
            location.replace(http_request.responseText);
        } else {
            alert(http_request.status);
        }
    }
}


function Complete(bought_id)
{
    makeRequest("/shop/bought/complet/", "POST", "&bought_id=" + bought_id);
}

(function ($) {
    $(document).ready(function ($) {
        $(".object-tools").append('<li><a href="/shop/getfile/" class="addlink">Get Raport</a></li>');
    });
})(django.jQuery);