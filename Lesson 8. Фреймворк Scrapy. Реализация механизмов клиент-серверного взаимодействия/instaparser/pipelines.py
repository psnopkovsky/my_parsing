
from itemadapter import ItemAdapter
import scrapy
from pymongo import MongoClient

class InstaparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongobase = client.instagram

    def process_item(self, item, spider):
        if item.get('type_') == 'followers':
            collection_followers = self.mongobase[item.get('username')]
            collection_followers.insert_one(item)
        else:
            collection_following = self.mongobase[item.get('username')]
            collection_following.insert_one(item)
        return item
