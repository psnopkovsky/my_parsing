# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstaparserItem(scrapy.Item):
    user_id = scrapy.Field()
    username = scrapy.Field()

    pk_followers = scrapy.Field()
    name_followers = scrapy.Field()
    full_name_followers = scrapy.Field()
    followers_data = scrapy.Field()

    pk_following = scrapy.Field()
    name_following = scrapy.Field()
    full_name_following = scrapy.Field()
    following_data = scrapy.Field()

    type_ = scrapy.Field()
    _id = scrapy.Field()
