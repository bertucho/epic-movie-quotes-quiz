# Stdlib imports
from django.db import models

# Create your models here.
class Movie(models.Model):
	title = models.CharField(max_length=200)
	original_title = models.CharField(max_length=200,default="")
	year = models.IntegerField()
	imdb_score = models.DecimalField(max_digits = 3, decimal_places = 1)
	votes = models.IntegerField()
	posterPath = models.CharField(max_length=200)

	def __unicode__(self):
		return self.title

class Quote(models.Model):
	movie = models.ForeignKey(Movie)
	text = models.CharField(max_length=1024)
	mf_visits = models.IntegerField()
	score = models.DecimalField(max_digits = 4, decimal_places = 1)
	popularity_rank = models.DecimalField(max_digits = 6, decimal_places = 1)
	level = models.IntegerField()

	def __unicode__(self):
		return self.text