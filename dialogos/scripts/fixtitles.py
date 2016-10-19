from quotes.models import Movie, Quote
import requests

apiurl = 'http://api.myapifilms.com/imdb/idIMDB?token=e800ad37-f86c-429d-b48e-404f4a114154&format=json&language=es-es&filter=3&exactFilter=1&limit=10&title='

for movie in Movie.objects.all().iterator():
	error = open("error-movies","w")
	movies_changed = open("movies-changed","w")
	original_title_file = open("original-titles","w")
	wrong_year = open("wrong-year","w")
	apiresp = requests.get(apiurl+movie.title).json()
	if 'error' in apiresp or not 'data' in apiresp or not apiresp['data']['movies']:
		print 'Error buscando: '+movie.title
		error.write(movie.title+"\n")
	#si la api ha devuelto error
	else:
		apimovie = apiresp['data']['movies'][0]
		#si coincide el año suponemos que es la misma peli
		if movie.year == int(apimovie['year']):
			#si en la bd tenemos un titulo distinto
			if movie.title != apimovie['title']:
				#lo escribimos en nuestro archivo debug
				movies_changed.write(movie.title)
				for i in range(len(movie.title),73): #rellenamos con -
					movies_changed.write('-')
				movies_changed.write(apimovie['title']+'\n')
				movie.title = apimovie['title'] #lo cambiamos en nuestra instancia
				movie.save(update_fields=['title']) #actualizamos en la bd
			#añadimos el titulo original que antes no habia
			movie.original_title = apimovie['originalTitle']
			movie.save(update_fields=['original_title']) #actualizamos en la bd
			#lo escribimos en nuestro archivo para que quede constancia
			original_title_file.write(movie.title)
			for i in rante(len(movie.title),73): #rellenamos con '-'
				original_title_file.write('-')
			original_title_file.write(movie.original_title+'\n')
		else: # si no coincide el año
			#lo escribimos en otro archivo para que quede constancia
			movie_year = movie.title+' ('+str(movie.year)+') '
			wrong_year.write(movie.title+' ('+str(movie.year)+') ')
			for i in range(len(movie_year),73):
				wrong_year.write('-')
			wrong_year.write(apimovie['title']+' ('+apimovie['year']+')\n')