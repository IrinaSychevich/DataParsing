# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, Compose, TakeFirst

def process_price(price):
    try:
        price = price[0]
    except Exception as e:
        price = None
    return price

class AvitoparserItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    name = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(input_processor=Compose(process_price), output_processor=TakeFirst())
    photos = scrapy.Field()
    description = scrapy.Field(output_processor=TakeFirst())
    url = scrapy.Field(output_processor=TakeFirst())