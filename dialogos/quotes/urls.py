from django.conf.urls import patterns, url
from quotes import views
from views import *
 
urlpatterns = patterns('',
	url(r'^sdf$', index, name='index'),
	url(r'^$', GameView.as_view(), name='game'),
	url(r'^post$', AnswerView.as_view(), name='answer'),
	url(r'^edit$', QuoteUpdate.as_view(), name='update'),
)
