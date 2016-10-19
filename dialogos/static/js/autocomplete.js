

$(document).ready(function($){
	$('#id_title').autocomplete({
		source: getData,
		select: getInfo,
		focus: foco
	});
});


getData = function(request,response){
	var url = window.location.origin+"/myapifilms?q=";
	var title = request.term;
	
	url += title;

	$.get(url,function(data){
		var movies = JSON.parse(data)
		response(movies.data.movies.map(function(item) {
            return { 
                label: item.title+ " ("+item.year+")" + " - " + item.votes + " votes, " + item.rating,
                value: item
            };
        }));
        
	})
}

function getInfo(event, ui){
	var title = ui.item.value.title;
	var year = ui.item.value.year;
	var imdb_score = ui.item.value.rating.replace(',','.');
	var votes = ui.item.value.votes.replace(/[,.]/g,'');
	var poster_path = ui.item.value.urlPoster;
	console.log(votes);
	console.log(poster_path);
	console.log(imdb_score);

	$('#id_title').val(title);
	$('#id_year').val(year);
	$('#id_imdb_score').val(imdb_score);
	$('#id_total_votes').val(votes);
	$('#id_posterPath').val(poster_path);
	event.preventDefault();
}

function foco(event, ui){
	if(event.originalEvent.originalEvent.type === "keydown"){
		$(input_id).val(ui.item.value.title);
	}
	event.preventDefault();
}

/*

getData = function(request,response){
	var url = "https://api.themoviedb.org/3/search/movie?language=es&api_key=5216d9c936b95a2e739acb3c4b1b8adf&query=";
	var title = request.term;
	
	url += title;

	$.get(url,function(data){
		response($.map(data.results, function(item) {
			var date = new Date(item.release_date);
			var year = date.getFullYear();
			var label = item.title+ " ("+year+")";
            return { 
                label: label,
                value: item
            };
        }));
        
	})
}

function getInfo(event, ui){
	var title = ui.item.value.title;
	var date = ui.item.value.release_date;
	console.log(date);
	var id = ui.item.value.id;
	var poster_path = ui.item.value.poster_path;

	$('#id_title').val(title);
	$('#id_year').val(date);
	$('#id_tmdbId').val(id);
	$('#id_posterPath').val(poster_path);
	event.preventDefault();
}

function foco(event, ui){
	var title = ui.item.title;
	event.preventDefault();
}
*/