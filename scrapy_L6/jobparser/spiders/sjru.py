import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem

class SjruSpider(scrapy.Spider):
    name = "sjru"
    allowed_domains = ["superjob.ru"]
    start_urls = ["https://russia.superjob.ru/vacancy/search/?keywords=Python"]

    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[contains(@class,'f-test-link-Dalshe')]/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath("//div[contains(@class,'f-test-vacancy-item')]//a/@href").getall()
        for link in links:
            yield response.follow(link, callback=self.vacancy_parse)

    def vacancy_parse(self, response: HtmlResponse):
        name = response.xpath('//h1[contains(@class,"dJivP")]/text()').get()
        salary = response.xpath('//span[contains(@class, "_4Gt5t")]/span/text()').getall()
        url = response.url
        yield JobparserItem(name=name, salary=salary, url=url)