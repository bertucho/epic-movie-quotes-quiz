from django.contrib import admin
from quotes.models import Movie
from quotes.models import Quote
from django import forms

class QuoteForm(forms.ModelForm):
	text = forms.CharField(widget = forms.Textarea)
	class Meta:
		model = Quote
		fields = ['movie', 'text', 'popularity_rank', 'score', 'mf_visits', 'level']

class MovieAdmin(admin.ModelAdmin):
	search_fields = ['title']
	class Media:
		js = ('http://ajax.googleapis.com/ajax/libs/jquery/1.11.0/jquery.min.js',
			'/static/js/jquery-ui.min.js',
			'/static/js/autocomplete.js',
			)
		css = {'all': ('http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.4/themes/smoothness/jquery-ui.css',)}

class QuoteAdmin(admin.ModelAdmin):
	list_display = ('text', 'get_movie_title', 'popularity_rank', 'score', 'level')
	search_fields = ['text', 'movie__title']
	form = QuoteForm

	def get_movie_title(self, obj):
		return obj.movie.title
	get_movie_title.short_description = 'Movie'
	get_movie_title.admin_order_field = 'movie__title'


admin.site.register(Movie, MovieAdmin)
admin.site.register(Quote, QuoteAdmin)