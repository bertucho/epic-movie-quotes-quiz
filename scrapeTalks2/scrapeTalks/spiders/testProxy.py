import scrapy

class TalkspiderSpider(scrapy.Spider):
    name = "testProxy"
    allowed_domains = ["whatismyip.com"]
    start_urls = (
        'http://www.whatismyip.com',
    )

    def parse(self, response):
    	open('test.html', 'wb').write(response.body)
