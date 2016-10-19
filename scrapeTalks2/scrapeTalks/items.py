# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy_djangoitem import DjangoItem
from scrapy.item import Field

from quotes.models import Movie, Quote


class QuoteItem(DjangoItem):
    django_model = Quote

class MovieItem(DjangoItem):
	django_model = Movie
