// This function gets cookie with a given name
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

/*
The functions below will create a header with csrftoken
*/

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
function sameOrigin(url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
            // Send the token to same-origin, relative URLs only.
            // Send the token only if the method warrants CSRF protection
            // Using the CSRFToken value acquired earlier
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});



/* Project specific Javascript goes here. */
var input_id = '#id_respuesta';

$(document).ready(function($){
	$(input_id).autocomplete({
		source: getData,
		select: getInfo,
		focus: foco
	});
	$('#answer').submit(function(event){
		event.preventDefault();
		$.post("post", {respuesta: $(input_id).val()}, function(data){
			if(data.correct)
				$('#result').html("Correcto!");
			else
				$('#result').html(data.title);
			$('#enviar').click(function(event){
				event.preventDefault();

			});
			$('#enviar').val("Siguiente");
		});		
	});
});

getData = function(request,response){
	var url = "../movies?q=";
	var title = request.term;
	
	url += title;

	$.get(url,function(data){
		var movies = JSON.parse(data)
		response(movies.map(function(item) {
            return { 
                label: item.title+ " ("+item.year+")",
                value: item
            };
        }));
        
	})
}

function getInfo(event, ui){
	var title = ui.item.value.title;
	var year = ui.item.value.year;
	console.log(year);

	$(input_id).val(title);
	/*$('#id_year').val(date);
	$('#id_tmdbId').val(id);
	$('#id_posterPath').val(poster_path);*/
	event.preventDefault();
}

function foco(event, ui){
	if(event.originalEvent.originalEvent.type === "keydown"){
		$(input_id).val(ui.item.value.title);
	}
	event.preventDefault();
}
