import scrapy
from scrapy.http import HtmlResponse
from shopparser.items import ShopparserItem
from scrapy.loader import ItemLoader

class CastaramaSpider(scrapy.Spider):
    name = "castorama"
    allowed_domains = ["castorama.ru"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start_urls = [f"https://www.castorama.ru/catalogsearch/result/?q={kwargs.get('query')}"]

    def parse(self, response: HtmlResponse):

        links = response.xpath('//a[contains(@class,"product-card__name")]')
        if links:
            for link in links:
                yield response.follow(link, callback=self.parse_object)
        next_page = response.xpath("//a[@class='next i-next']/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)


    def parse_object(self, response:HtmlResponse):

        loader = ItemLoader(item=ShopparserItem(), response=response)
        loader.add_xpath('name', '//h1[contains(@class,"product-essential__name")]/text()')
        loader.add_xpath('price', "//span[@class='price']/span/span/text()")
        loader.add_xpath('photos', "//div[@class='js-zoom-container']/img[contains(@class,'top-slide__img')]/@data-src")
        loader.add_value('url', response.url)
        loader.add_xpath('specifications_labels', "//div[contains(@class, 'product-block product-specifications')]//dt[contains(@class, 'specs-table__attribute-label')]/span/text()")
        loader.add_xpath('specifications_values', "//div[contains(@class, 'product-block product-specifications')]//dd[contains(@class, 'specs-table__attribute-value')]/text()")
        yield loader.load_item()