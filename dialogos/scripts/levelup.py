from quotes.models import Quote, Movie
from django.db.models import F

Quote.objects.all().update(level=F('level')+5)