import scrapy
from scrapy.responsetypes import Response
from tripadvisor.items import Item


class Review(scrapy.Spider):
    name = "tripadvisor"
    start_urls = ["https://www.tripadvisor.com/Hotels-g295366-Antigua_Sacatepequez_Department-Hotels.html"]

    def parse(self, response):
        urls = []
        for href in response.css('div.meta_listing').xpath('@data-url').extract():
            url = response.urljoin(href)
            if url not in urls:
                urls.append(url)

                yield scrapy.Request(url, callback=self.parse_page)

        next_page = response.css("a.nav.next").xpath('@href').get()
        if next_page:
            url = response.urljoin(next_page)

            yield scrapy.Request(url, callback=self.parse)

    def parse_page(self, response: Response):

        sub_div = response.css('div.cqoFv')

        for review in sub_div:
            item = Item()

            contents = review.css('q.XllAv span::text').get()
            content = contents.encode("utf-8")

            ratings = review.css('span.ui_bubble_rating').xpath('@*').get()
            rating = int(ratings.split(' ')[-1].replace('bubble_', ''))

            item['rating'] = rating
            item['review'] = content
            yield item

        next_page = response.css("a.nav.next").xpath('@href').get()
        if next_page:
            url = response.urljoin(next_page)
            yield scrapy.Request(url, self.parse_page)
