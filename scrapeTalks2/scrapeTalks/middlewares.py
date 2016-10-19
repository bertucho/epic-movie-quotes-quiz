import scrapy
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.downloadermiddlewares.httpproxy import HttpProxyMiddleware

import telnetlib
import time
import random
import logging

from settings import USER_AGENT_LIST

logger = logging.getLogger(__name__)

class ProxyMiddleware(object):
    # overwrite process request
    def process_request(self, request, spider):
    	#if spider['name'] == talkspider:
    		#if "google." in request.url:
		        # Set the location of the proxy
		        #request.meta['proxy'] = "http://localhost:8123"
		#else:
		request.meta['proxy'] = "http://localhost:8123"

class RetryChangeProxyMiddleware(object):
    def process_request(self, request, spider):
        if random.choice(xrange(1,100)) <= 5:
            logger.info('Changing proxy')
            tn = telnetlib.Telnet('127.0.0.1', 9051)
            tn.read_until("Escape character is '^]'.", 2)
            tn.write('AUTHENTICATE "hola"\r\n')
            tn.read_until("250 OK", 2)
            tn.write("signal NEWNYM\r\n")
            tn.read_until("250 OK", 2)
            tn.write("quit\r\n")
            tn.close()
            logger.info('>>>> Proxy changed. Sleep Time')
            time.sleep(3)



# 30% useragent change
class RandomUserAgentMiddleware(object):
    def process_request(self, request, spider):
        if random.choice(xrange(1,100)) <= 25:
            logger.info('Changing UserAgent')
            ua  = random.choice(USER_AGENT_LIST)
            if ua:
                request.headers.setdefault('User-Agent', ua)
            logger.info('>>>> UserAgent changed: '+ua)