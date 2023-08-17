import scrapy
from scrapy_splash import SplashRequest
from avitoparser.items import AvitoparserItem
from scrapy.loader import ItemLoader



class AvitoSpider(scrapy.Spider):
    name = "avito"
    allowed_domains = ["avito.ru"]
    start_urls = ["https://www.avito.ru/izhevsk?q=котята"]
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.page = 1
        self.start_urls = [f"https://www.avito.ru/izhevsk?p={self.page}&q={kwargs.get('query')}"]

    def start_requests(self):
        if not self.start_urls and hasattr(self, "start_url"):
            raise AttributeError(
                "Crawling could not start: 'start_urls' not found "
                "or empty (but found 'start_url' attribute instead, "
                "did you miss an 's'?)"
            )
        for url in self.start_urls:
            yield SplashRequest(url)

    def parse(self, response):
        links = response.xpath("//a[@data-marker='item-title']/@href").getall()
        if links:
            for link in links:
                yield SplashRequest("https://avito.ru" + link, callback=self.parse_ads)
            next_p = int(response.url.split('p=')[1].split('&q=')[0]) + 1
            next_page = f'{response.url.split("p=")[0]}p={next_p}&q={response.url.split("p=")[1].split("&q=")[1]}'
            yield SplashRequest(next_page, callback=self.parse)


    def parse_ads(self, response):

        loader = ItemLoader(item=AvitoparserItem(), response=response)
        loader.add_xpath('name', "//span[@class='title-info-title-text']/text()")
        loader.add_xpath('price', "//span[@data-marker='item-view/item-price']/@content")
        loader.add_xpath('photos', "//div[@data-marker='image-frame/image-wrapper']/img/@src |"
                                        "//li[@data-marker='image-preview/item']/img/@src")
        loader.add_value('url', response.url)
        loader.add_xpath('description', "//div[@data-marker='item-view/item-description']/p/text()")
        yield loader.load_item()