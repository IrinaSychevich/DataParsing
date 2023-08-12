# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import scrapy
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient

class ShopparserPipeline:
    def __init__(self):
        client = MongoClient(host='localhost', port=27017)
        self.mongo_base = client.shop_castorama
    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        item = self.specifications_item(item)
        collection.insert_one(item)
        return item

    def specifications_item(self, item):
        item['specifications'] = dict(zip(item['specifications_labels'], item['specifications_values']))
        del item['specifications_labels']
        del item['specifications_values']
        return item

class ObjectPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for photo in item['photos']:

                try:
                    meta = {'image_name': item["name"]}
                    yield scrapy.Request(photo, meta=meta)
                except Exception as e:
                    print(e)


    def file_path(self, request, response=None, info=None):
        return '%s/%s.jpg' % (request.meta['image_name'], request.url.split('/')[6])

    def item_completed(self, results, item, info):
        if results:
            item['photos'] = [itm[1] for itm in results if itm[0]]
        return item



