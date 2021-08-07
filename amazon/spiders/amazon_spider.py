import scrapy
from ..items import AmazonItem
from scrapy.http import Request

class AmazonSpiderSpider(scrapy.Spider):

    name = 'amazon'

    def __init__(self,search_key,number_of_pages=20):

        self.pag_num = 2
        self.number_of_pages = int(number_of_pages)
        url = 'https://www.amazon.com/s?k={}'.format(search_key)
        self.start_urls = [url]
        self.item = AmazonItem()
        self.search_key = search_key


        super().__init__()

    def parse(self, response):


        titles = response.css('.a-size-medium::text').extract()
        links = response.css('.s-line-clamp-2').css('.a-link-normal.a-text-normal::attr(href)').extract()

        img_link = response.css('.s-image').css('::attr(src)').extract()

        print(len(links),len(titles),len(img_link))
        for i in range(len(links)):

            request = Request("https://www.amazon.com"+links[i],callback=self.scrape_inner, meta=dict(links=links[i],img_link=img_link[i],title=titles[i]))


            yield request


        while self.pag_num <= self.number_of_pages :
            url = 'https://www.amazon.com/s?k={}&page={}&qid=1627921842&ref=sr_pg_{}'.format(self.search_key,self.pag_num,self.pag_num)
            self.pag_num += 1
            yield response.follow(url,callback=self.parse)



    def scrape_inner(self,response):


        self.item['title'] = response.meta['title']
        self.item['links'] = response.meta['links']
        self.item['img_link'] = response.meta['img_link']

        over_all = response.css('#priceblock_ourprice_row .a-span12')
        # productOverview_feature = response.css('#productOverview_feature_div .a-text-bold').css('::text').extract()

        # productOverview_values = response.css('.a-span9 .a-size-base').css('::text').extract()

        price = over_all.css('#priceblock_ourprice').css('::text').extract()
        shipping = over_all.css('a-size-base a-color-secondary').css('::text').extract()
        feature_list = response.css('#productOverview_feature_div .a-size-base')
        productOverview_feature = feature_list.xpath("//td[@class='a-span3']/text()")
        productOverview_values = feature_list.xpath("//td[@class='a-span9']/text()")

        if len(price) == 0:

            price = 0.0

        else :

            price = float(price[0].split('$')[1])

        feauture = ''

        for i in range(len(productOverview_feature)):

            feauture +=  productOverview_feature[i] + ' : ' + productOverview_values[i] + ' , '

        feauture = feauture[:-3]
        #feature-bullets li

        About = response.css('#feature-bullets li').css('::text').extract()
        About = ' , '.join(About)
        # shipping = response.css('#ourprice_shippingmessage .a-color-secondary').css('::text').extract()
        if len(shipping) != 0:

            shipping = shipping.split()[0]
            shipping = float(shipping.split('$')[1])

        else:

            shipping = 0.0


        self.item['price'] = price
        self.item['feauture'] = feauture
        self.item['About'] = About
        self.item['shipping'] = shipping



        return self.item
