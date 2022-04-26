import scrapy
from scrapy.http import HtmlResponse
from leroyparser.items import LeroyparserItem
from scrapy.loader import ItemLoader

class LmruSpider(scrapy.Spider):
    name = 'lmru'
    allowed_domains = ['castorama.ru']

    def __init__(self, name = None, **kwargs):
        super().__init__(name, **kwargs)
        self.start_urls = [f"https://www.castorama.ru/tools/power-tools/{kwargs.get('query')}"]


    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[@class='next i-next']/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath("//a[@class = 'product-card__img-link']/@href")
        for link in links:
            yield response.follow(link, callback = self.parse_ads)

    def parse_ads(self, response: HtmlResponse):
        loader = ItemLoader(item=LeroyparserItem(), response=response)
        loader.add_xpath('name', "//h1[@class = 'product-essential__name hide-max-small']/text()")
        loader.add_xpath('price', "//span[@class = 'price']//text()")
        loader.add_xpath('photos', "//ul[@class='swiper-wrapper']//span/@content")
        loader.add_value('url', response.url)
        yield loader.load_item()
