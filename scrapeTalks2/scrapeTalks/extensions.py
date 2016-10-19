from scrapy import signals
import logging
from scrapy.core.downloader import Slot

logger = logging.getLogger(__name__)
failed_title = object()

class CustomDelay:

	def __init__(self, crawler):
		self.crawler = crawler

		crawler.signals.connect(self._spider_opened, signal=signals.spider_opened)

	@classmethod
	def from_crawler(cls, crawler):
		return cls(crawler)

	def _spider_opened(self, spider):
		custom_slots = self.crawler.settings.get('CUSTOMDELAY_SLOTS')
		downloader = self.crawler.engine.downloader
		for key, delay in custom_slots.iteritems():
			if key in downloader.slots:
				slot = downloader.slots.get(key)
				slot.delay = delay
				slot.randomize_delay = delay
			else:
				conc = self.ip_concurrency if downloader.ip_concurrency else downloader.domain_concurrency
				downloader.slots[key] = Slot(conc, delay, self.crawler.settings)
				print '\n\nSlot: '+key+', '+str(delay)+'\n\n'


class Fails:

	def __init__(self, crawler):
		self.crawler = crawler
		self.failed_titles = []

		crawler.signals.connect(self._spider_closed, signal=signals.spider_closed)
		crawler.signals.connect(self._failed_title, signal=failed_title)

	@classmethod
	def from_crawler(cls, crawler):
		return cls(crawler)

	def _failed_title(self, title):
		print '\nAnyadido titulo fallido\n\n'
		self.failed_titles.append(title)
		self.crawler.stats.inc_value('failed_titles_count')

	def _spider_closed(self, spider):
		print '\n Cerrando spider\n\n'+'\n'.join(self.failed_titles)
		open('failedtitles','w').write('\n'.join(self.failed_titles).encode('utf-8'))