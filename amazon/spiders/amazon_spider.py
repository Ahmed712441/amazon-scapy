import scrapy
from ..items import AmazonItem
from scrapy.http import Request
from tensorflow.keras.models import model_from_json
import cv2
import urllib
import numpy as np

class AmazonSpider(scrapy.Spider):

    name = 'amazon'

    def __init__(self,search_key,number_of_pages=20):

        self.num_to_char = {0: 'A',1: 'B',2: 'C',3: 'D',4: 'E',5: 'F',6: 'G',7: 'H',8: 'I',9: 'J',10: 'K',11: 'L',12: 'M',13: 'N',14: 'O',15: 'P',16: 'Q',17: 'R',18: 'S',19: 'T',20: 'U',21: 'V',22: 'W',23: 'X',24: 'Y',25: 'Z'}
        json_file = open('D:/rename/model_json/captcha.json', 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        self.loaded_model = model_from_json(loaded_model_json)
        self.loaded_model.load_weights("D:/rename/model_json/captcha.h5")
        self.pag_num = 2
        self.number_of_pages = int(number_of_pages)
        url = 'https://www.amazon.com/s?k={}'.format(search_key)
        self.start_urls = [url]
        # self.item = AmazonItem()
        self.search_key = search_key
        self.charachters = ["!","#","$","&","'","("	,")",	"*",	"+"	, ","	, "/"	,":"	,";"	,"="	,"?"	,"@" ,"["	,"]"]
        self.replace_with = ['%21'	,'%23',	'%24'	,'%26',	'%27'	,'%28',	'%29'	,'%2A'	,'%2B'	,'%2C',	'%2F'	,'%3A',	'%3B',	'%3D',	'%3F',	'%40'	,'%5B',	'%5D']


        super().__init__()

    def predict(self,img):

        prediction = self.loaded_model.predict(img.reshape(1,70,200,1))
        word = ""
        for i in range(len(prediction)):
            word += self.num_to_char[np.argmax(prediction[i])]

        return word


    def parse(self, response):

        if len(response.xpath("//input[@id='captchacharacters']").extract()) != 0:

            print('solving')

            url = self.captcha_solver(response)

            yield response.follow(url,callback=self.parse)

        else:

            titles = True

            titles = response.css('.a-size-medium.a-text-normal::text').extract()
            links = response.css('.sg-col-12-of-20 .s-line-clamp-2').css('.a-link-normal.a-text-normal::attr(href)').extract()

            img_link = response.css('.s-image-fixed-height .s-image').css('::attr(src)').extract()

            # print(len(links),len(titles),len(img_link))
            if(len(links) == 0):

                titles = False
                links =  response.css('.a-size-mini.a-spacing-none.a-color-base.s-line-clamp-4').css('.a-link-normal.a-text-normal::attr(href)').extract()
                # print(len(.extract()))
            print(len(links))
            for i in range(len(links)):

                if titles:

                    yield Request("https://www.amazon.com"+links[i],callback=self.scrape_inner, meta=dict(links=links[i],img_link=img_link[i],title=titles[i]))

                else:

                    yield Request("https://www.amazon.com"+links[i],callback=self.scrape_inner, meta=dict(links=links[i],img_link=None,title=None))

            while self.pag_num <= self.number_of_pages :
                url = 'https://www.amazon.com/s?k={}&page={}&qid=1627921842&ref=sr_pg_{}'.format(self.search_key,self.pag_num,self.pag_num)
                self.pag_num += 1
                yield response.follow(url,callback=self.parse)



    def scrape_inner(self,response):



        if len(response.xpath("//input[@id='captchacharacters']").extract()) != 0:

            url = self.captcha_solver(response)

            print('STUCK')

            yield response.follow(url,callback=self.scrape_inner)


        else:

            if not response.meta['title']:

                response.meta['title'] =  response.css('#productTitle::text').extract()[0]


            if not response.meta['img_link']:

                response.meta['img_link'] = response.css('#imgTagWrapperId').css('::attr(src)').extract()[0]


            item = AmazonItem()
            item['title'] = response.meta['title']
            item['links'] = response.meta['links']
            item['img_link'] = response.meta['img_link']

            over_all = response.css('#priceblock_ourprice_row .a-span12')

            price = over_all.css('#priceblock_ourprice').css('::text').extract()
            shipping = over_all.css('a-size-base a-color-secondary').css('::text').extract()

            productOverview_feature = response.css('#productOverview_feature_div .a-text-bold').css('::text').extract()

            productOverview_values = response.css('.a-span9 .a-size-base').css('::text').extract()


            if len(price) == 0:

                price = 0.0

            else :
                price = price[0].split('$')[1]
                price = price.split(',')
                price = ''.join(price)
                price = price.split(' -')[0]
                price = float(price)

            feauture = ''

            for i in range(len(productOverview_feature)):

                feauture +=  productOverview_feature[i] + ' : ' + productOverview_values[i] + ' , '

            feauture = feauture[:-3]


            About = response.css('#feature-bullets li').css('::text').extract()
            About = ' , '.join(About)

            if len(shipping) != 0:

                shipping = shipping.split()[0]
                shipping = float(shipping.split('$')[1])

            else:

                print('NOSHIPPING')
                shipping = 0.0


            item['price'] = price
            item['feauture'] = feauture
            item['About'] = About
            item['shipping'] = shipping

            # print('PASSED')

            yield item



    def convert(self,string):


        for i in range(len(self.charachters)):
            string = string.replace(self.charachters[i],self.replace_with[i])

        return string


    def captcha_solver(self,response):

        amzn = response.xpath("//input[@name='amzn']").css("::attr(value)").extract()[0]
        amzn_r = response.xpath("//input[@name='amzn-r']").css("::attr(value)").extract()[0]

        image_url = response.css('.a-row.a-text-center').css('img::attr(src)').extract()[0]

        req = urllib.request.urlopen(image_url)
        arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
        img = cv2.imdecode(arr, -1)

        prediction = self.predict(img)
        # print(prediction)
        amzn = self.convert(amzn)
        amzn_r = self.convert(amzn_r)
        url = f'https://www.amazon.com/errors/validateCaptcha?amzn={amzn}&amzn-r={amzn_r}&field-keywords={prediction}'

        return url
