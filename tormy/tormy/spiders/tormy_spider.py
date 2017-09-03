import scrapy
import logging
from tormy.items import TormyItem

class TorrentSpider(scrapy.Spider):
    custom_settings = {
        # PIPELINES must be registered here and in settings.py
        'ITEM_PIPELINES': {
            'tormy.pipelines.JsonWriterPipeline': 300,
        },
        # LOG_ENABLED must be made True here and in settings.py to view logs.
        'LOG_ENABLED': 'False',
    }
    # 'name' of the spider.
    name = "tormy"

    def __init__(self, query=None):
        # 'query' is entered by the user and recieved from tormy-cli.
        self.search_query = query


    def start_requests(self):
        urls = [
            'http://thepiratebay.torbox.net/search/{}'.format(self.search_query),
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)


    def parse(self, response):
        item = TormyItem()
        for row in response.css("#searchResult"):
            item['name'] = response.css('.detName a::text').extract()
            item['info'] = response.css('font.detDesc::text').extract()
            item['seeders'] = response.css('td.vertTh ~ td:nth-of-type(3)::text').extract()
            item['leechers'] = response.css('td.vertTh ~ td:nth-of-type(4)::text').extract()
            item['magnet'] = response.css('.detName ~ a:nth-of-type(1)::attr(href)').extract()

        item['info'] = [unit.replace(', ULed by', '') for unit in item['info']]
        yield item