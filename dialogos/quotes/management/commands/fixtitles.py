# -*- coding: utf-8 -*-

from optparse import make_option
from quotes.models import Movie, Quote
import requests
from django.core.management.base import NoArgsCommand

class Command(NoArgsCommand):

    help = "Whatever you want to print here"

    option_list = NoArgsCommand.option_list + (
        make_option('--verbose', action='store_true'),
    )

    def handle_noargs(self, **options):
		apiurl = 'http://api.myapifilms.com/imdb/idIMDB?token=e800ad37-f86c-429d-b48e-404f4a114154&format=json&language=es-es&filter=3&exactFilter=1&limit=10&title='
		to_change = []
		originals = []
		error = open("error-movies","w")
		movies_changed = open("movies-changed","w")
		original_title_file = open("original-titles","w")
		not_original_title_file = open("not-original-titles","w")
		wrong_year = open("wrong-year","w")
		for movie in Movie.objects.all():
			apiresp = requests.get(apiurl+movie.title).json()
			if 'error' in apiresp or not 'data' in apiresp or not apiresp['data']['movies']:
				print 'Error buscando: '+movie.title
				error.write(movie.title.encode("utf-8")+"\n")
			#si la api ha devuelto error
			else:
				apimovie = apiresp['data']['movies'][0]
				#si coincide el anyo suponemos que es la misma peli
				if str(movie.year) == apimovie['year']:
					#si en la bd tenemos un titulo distinto
					if movie.title != apimovie['title']:
						#lo escribimos en nuestro archivo debug
						movies_changed.write(movie.title.encode("utf-8"))
						for i in range(len(movie.title),73): #rellenamos con -
							movies_changed.write('-')
						movies_changed.write(apimovie['title'].encode("utf-8")+'\n')
						movie.title = apimovie['title'] #lo cambiamos en nuestra instancia
						movie.save #actualizamos en la bd
					#añadimos el titulo original que antes no habia
					if apimovie['originalTitle']:
						movie.original_title = apimovie['originalTitle']
						movie.save() #actualizamos en la bd
						#lo escribimos en nuestro archivo para que quede constancia
						original_title_file.write(movie.title.encode("utf-8"))
						for i in range(len(movie.title),73): #rellenamos con '-'
							original_title_file.write('-')
						original_title_file.write(movie.original_title.encode("utf-8")+'\n')
					else:
						not_original_title_file.write(movie.title.encode('utf-8')+'\n')
				else: # si no coincide el anyo
					#lo escribimos en otro archivo para que quede constancia
					movie_year = movie.title.encode("utf-8")+' ('+str(movie.year)+') '
					wrong_year.write(movie_year)
					for i in range(len(movie_year),73):
						wrong_year.write('-')
					wrong_year.write(apimovie['title'].encode("utf-8")+' ('+apimovie['year'].encode("utf-8")+')\n')
		error.close()
		movies_changed.close()
		original_title_file.close()
		wrong_year.close()