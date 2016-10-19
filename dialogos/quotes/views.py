# Stdlib imports
from __future__ import absolute_import
from random import randint
import json
import requests

# Core Django imports
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseForbidden
from django.template import RequestContext, loader
from django.core import serializers
from django import forms
from django.views.generic import TemplateView, UpdateView
from django.views.generic import View
from django.views.generic.edit import FormMixin, ProcessFormView
# Third-party app imports

# Imports from your apps
from .models import Quote, Movie

class AnswerForm(forms.Form):
	respuesta = forms.CharField(max_length=200, required=False)

class EditQuoteForm(forms.Form):
	text = forms.CharField(max_length=1024)
	level = forms.IntegerField()


# Create your views here.
def index(request):
	if request.method == 'POST':
		form = AnswerForm(request.POST)
		if form.is_valid():
			title = form.cleaned_data['respuesta']
			rightMovies = Quote.objects.filter()
	else:
		quote = getRandQuote()
		print'\n\n%s\n' %quote
		template = loader.get_template('../templates/base.html')
		return render(request,"../templates/game/question.html",{'quote':quote})


def getMovies(request):
	if request.user.is_authenticated():
		query = request.GET.get('q', '')
		if query != '':
			movies = Movie.objects.filter(title__icontains=query)
			result = []
			for movie in movies:
				movie_dict = {'title': movie.title, 'year': movie.year}
				result.append(movie_dict)

			return HttpResponse(json.dumps(result))
		else:
			return HttpResponse("Invalid query")
	else:
		return HttpResponse("Debe iniciar sesion")


def myapifilms(request):
	if request.user.is_superuser:
		query = request.GET.get('q', '')
		if query != '':
			return HttpResponse(requests.get("http://api.myapifilms.com/imdb/idIMDB?token=e800ad37-f86c-429d-b48e-404f4a114154&format=json&language=es-es&filter=3&exactFilter=0&limit=10&title="+query))
		else:
			return HttpResponse("Consulta incorrecta")
	else:
		return HttpResponseForbidden()


class GameView(TemplateView):
	template_name = 'game/question.html'

	#sobreescribimos funcion para pasarle el contexto al template
	def get_context_data(self, **kwargs):
		# importante: llamamos a la funcion del padre
		context = super(GameView, self).get_context_data(**kwargs)
		# Variables que pasaremos
		form = AnswerForm()
		is_auth = False
		name = None
		dialogo = None
		level = 0


		# Si el usuario esta autenticado
		if self.request.user.is_authenticated():
			is_auth = True
			name = self.request.user.username   # Nombre del usuario
			quote = getRandQuote() 				# Recibimos una fila random de una quote de la bd
			if quote != None:
				dialogo = quote.text				# este sera el texto

				# Inicializamos variables de sesion para saber que pregunta esta respondiendo
				self.request.session['id'] = quote.id
				self.request.session['answer_expected'] = True

				if self.request.user.is_superuser:
					level = quote.level
					print level

		# Creamos el diccionario
		data = {
			'is_auth': is_auth,
			'name': name,
			'dialogo': dialogo,
			'form': form,
			'level': level
		}
		
		# Actualizamos el contexto (no creamos uno nuevo)
		context.update(data)

		return context


class QuoteUpdate(UpdateView):
	model = Quote
	#form_class = EditQuoteForm
	fields = ['text', 'level']
	success_url = '/game'

	def get_object(self):
		return Quote.objects.get(pk=self.request.session['id'])


class AnswerView(FormMixin, ProcessFormView):

	form_class = AnswerForm
	success_url = '/game'
	# Si el formulario es valido
	def form_valid(self, form):
		if not self.request.session['answer_expected']:
			return HttpResponseForbidden()

		# Para evitar multiples submits
		self.request.session['answer_expected'] = False
		rightMovie = getRightMovie(self.request.session['id'])
		print [attrib for attrib in form.__dict__.keys()]
		if form.cleaned_data['respuesta'] == rightMovie:
			return HttpResponse(json.dumps({'correct': True}), content_type="application/json")
		else:
			return HttpResponse(json.dumps({'correct': False, 'title': rightMovie}), content_type="application/json")

	def form_invalid(self, form):
		print'\ninvalid'
		response_data = {}
		response_data['result'] = 'invalid'
		return HttpResponse(json.dumps(response_data), content_type="application/json")


def getRandQuote():
	# Numero de dialogos en la bd
	len = Quote.objects.count()
	if len <= 0:
		return None
	N = randint(0,len-1)
	print '\n\n%d\n\n' % N
	# Consulta SQL (la opcion que nos da django es mas lenta)
	query = 'SELECT * FROM quotes_quote OFFSET '+str(N)+' LIMIT 1'
	row = Quote.objects.raw(query)
	return row[0]


def getRightMovie(id):
	quote = Quote.objects.get(pk=id)

	print'\n%s\n' %quote.movie.title
	return quote.movie.title

