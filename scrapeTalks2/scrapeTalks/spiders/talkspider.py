# -*- coding: utf-8 -*-
import scrapy
from scrapeTalks.items import *
#from scrapeTalks.settings import DEFAULT_REQUEST_HEADERS
from decimal import Decimal
from quotes.models import Movie
from scrapeTalks.extensions import failed_title
import re
import urllib2, urllib, requests


class TalkspiderSpider(scrapy.Spider):
    name = "talkspider"
    allowed_domains = []
    start_urls = ()
    MIN_VOTES = 80000
    apiurl = ''

    def parse_imdb(self, response):
        if response.css("form[action='CaptchaRedirect']"):
        	self.logger.error("Google Captcha")
    		raise scrapy.exceptions.CloseSpider("google Captcha")
    	movie = MovieItem()
        movie['title'] = response.meta['title']
        movie['title'].encode('utf-8')
        movie['year'] = int(response.xpath("//h3[1]//text()").re(r"\(([0-9]{4})\)")[-1])
        rich_snippet = response.css(".slp::text")

        # si no se encuentra el rich snippet
        if not rich_snippet:
	        self.logger.error("rich snippet")
	        raise scrapy.exceptions.IgnoreRequest('rich snippet')

        rich_snippet = rich_snippet[0]
        movie['imdb_score'] = float(rich_snippet.re(r"[0-9],?[0-9]?")[0].replace(',','.'))
        movie['total_votes'] = int(rich_snippet.re(r"[0-9\.]*\.?[0-9]{1,3}")[-1].replace('.',""))
        if movie['total_votes'] >= self.MIN_VOTES:
        	movie_instance = movie.save()
        	#procesamos la url de la pelicula en parse_pagination pues puede tener varias paginas
        	yield scrapy.Request(response.meta['movie_url'], 
        		meta={'movie': movie_instance, 'callback': 'parse_movie'}, 
        		callback = self.parse_pagination)

    def parse(self, response):
    	for letter_href in response.css("#movie-letters a::attr(href)"):
    		full_letter_url = response.urljoin(letter_href.extract())
    		print full_letter_url+'\n'
    		yield scrapy.Request(full_letter_url, meta={'callback': 'parse_page'}, callback=self.parse_pagination)

    def parse_pagination(self, response):
    	callback = getattr(self, response.meta['callback'])
    	last_page_url = response.css(".fc-pagination li[class='last-page'] a::attr(href)").extract()
    	if not last_page_url:
    		#response.meta['callback'](response)
    		yield scrapy.Request(response.url, meta = response.meta, dont_filter = True, callback = callback)
    	else:
	    	last_page_object = re.search(r"[0-9]*$",last_page_url[0])
	    	if not last_page_object:
	    		self.logger.error('No last_page (regex) '+response.url)
	    		raise scrapy.exceptions.IgnoreRequest('no last_page (regex)')

	    	last_page = int(last_page_object.group(0))
	    	base_page_url = response.urljoin(re.sub(r"[0-9]*$","",last_page_url[0]))
	     	for i in range(1,last_page+1):
	     		page_url = base_page_url+str(i)
	     		yield scrapy.Request(page_url, meta = response.meta, dont_filter = True, callback = callback)

#parse_page
    def parse_page(self, response):
		for movie_selector in response.css(".movies-grid li a"):
			movie_url = response.urljoin(movie_selector.css("a::attr(href)").extract()[0])
			movie_title = movie_selector.css("a span::text").extract()[0]
			if Movie.objects.filter(title = movie_title).exists():
				self.logger.error(''+movie_title+' already exists')
				continue
			
			apifilms_url = self.apiurl+movie_title.replace('&','%26').encode("utf-8")
			apiresp = requests.get(apifilms_url)
			apiresp = apiresp.json()
			if 'error' in apiresp or not 'data' in apiresp or not apiresp['data']['movies']:
				self.crawler.signals.send_catch_log(signal=failed_title, title=movie_title)
				self.logger.error(''+movie_title+'title failed in api')
				continue

			movie = MovieItem()
			movieresp = apiresp['data']['movies'][0]
			movie['title'] = movie_title
			movie['title'].encode('utf-8')
			movie['year'] = movieresp['year']
			print '\n'+movieresp['rating']+'\n\n'
			try:
				movie['imdb_score'] = float(movieresp['rating'].replace(',','.'))
			except:
				movie['imdb_score'] = 0.0
			try:
				movie['total_votes'] = int(movieresp['votes'].replace('.',''))
			except:
				movie['total_votes'] = 0

			if movie['total_votes'] >= self.MIN_VOTES:
				print '\nMinimos votos superados\n\n'
				movie_instance = movie.save()
				#procesamos la url de la pelicula en parse_pagination pues puede tener varias paginas
				yield scrapy.Request(movie_url, 
					meta={'movie': movie_instance, 'callback': 'parse_movie'}, 
					callback = self.parse_pagination)
	


    def parse_movie(self, response):
    	print '\n\naqui\n\n'
    	for quote_href in response.css(".detail a::attr(href)").extract():
    		quote_url = response.urljoin(quote_href)
    		yield scrapy.Request(quote_url, 
    			meta = {'movie': response.meta['movie']}, 
    			callback = self.parse_quote)

    def parse_quote(self, response):
    	quote = QuoteItem()
    	quote['movie'] = response.meta['movie']
    	quote['text'] = response.css("blockquote.current-phrase::text").extract()[0].strip()
    	details = response.css(".more-curiosity .content")
    	if not details:
    		self.logger.error('No details found')
    		raise scrapy.exceptions.IgnoreRequest('no visits found')

    	details = details[0]
    	visits = details.re(r"[0-9]+")
    	if not visits:
    		self.logger.error('No visits found (regex failed)')
    		raise scrapy.exceptions.IgnoreRequest('No visits found (regex failed)')

    	quote['mf_visits'] = int(visits[0]) #primer match
    	quote['score'] = float("{0:.1f}".format(self.get_score(quote['movie'].total_votes, quote['mf_visits'])))
    	quote['popularity_rank'] = float("{0:.1f}".format(self.get_popularity_rank(quote['movie'].total_votes, quote['mf_visits'])))
    	quote['level'] = self.get_level(quote['popularity_rank'])
    	quote.save()

    def get_score(self, votes, visits):
    	return float(votes/200000*visits/100)

    def get_level(self, popularity):
    	return int(100/popularity)

    def get_popularity_rank(self, votes, visits):
    	return float(votes/self.MIN_VOTES*visits)

