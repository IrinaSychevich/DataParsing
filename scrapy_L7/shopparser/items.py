# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, Compose, TakeFirst

def process_name(name):
    name = name[0].strip()
    return name

def process_price(price):
    try:
        price = price[0]
    except Exception as e:
        price = None
    return price

def process_photo(photo):
    photo = "https://www.castorama.ru" + photo.split()[0]
    return photo

def process_label(specification_label):
    specification_label = specification_label.strip()
    return specification_label

def process_value(specification_value):
    specification_value = specification_value.strip()
    return specification_value

class ShopparserItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    name = scrapy.Field(input_processor=Compose(process_name), output_processor=TakeFirst())
    price = scrapy.Field(input_processor=Compose(process_price), output_processor=TakeFirst())
    photos = scrapy.Field(output_processor=MapCompose(process_photo))
    url = scrapy.Field(output_processor=TakeFirst())
    image_name = scrapy.Field()
    specifications_labels = scrapy.Field(output_processor=MapCompose(process_label))
    specifications_values = scrapy.Field(output_processor=MapCompose(process_value))
    specifications = scrapy.Field()
