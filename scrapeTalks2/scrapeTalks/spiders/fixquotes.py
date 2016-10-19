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
    name = "fixquotes"
    allowed_domains = []
    start_urls = ()
    MIN_VOTES = 80000
    apiurl = ''


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
			yield scrapy.Request(movie_url, 
				meta={'callback': 'parse_movie'}, 
				callback = self.parse_pagination)



    def parse_movie(self, response):
    	print '\n\naqui\n\n'
    	for quote_href in response.css(".detail a::attr(href)").extract():
    		quote_url = response.urljoin(quote_href)
    		yield scrapy.Request(quote_url,  
    			callback = self.parse_quote)

    def parse_quote(self, response):
        text = response.css("blockquote.current-phrase::text").extract()
        first_line = text[0].strip()
        if first_line[-1] != '\"':
            print "yes\n"
            full_text = "\n".join(text).strip()
            if Quote.objects.filter(text=first_line).exists():
                Quote.objects.filter(text=first_line).update(text=full_text)

    def get_score(self, votes, visits):
    	return float(votes/200000*visits/100)

    def get_level(self, popularity):
    	return int(100/popularity)

    def get_popularity_rank(self, votes, visits):
    	return float(votes/self.MIN_VOTES*visits)

