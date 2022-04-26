# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from twisted.web.html import output
from itemloaders.processors import Compose, MapCompose, TakeFirst

def convert_price(value):
    value = value[0].replace(' ', '')
    value = int(value)
    return value

class LeroyparserItem(scrapy.Item):
    name = scrapy.Field(output_processor=TakeFirst())
    url = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(input_processor=TakeFirst(), output_processor=convert_price)
    photos = scrapy.Field()
    _id = scrapy.Field()

