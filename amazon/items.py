# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AmazonItem(scrapy.Item):
    # define the fields for your item here like:

    title = scrapy.Field()
    feauture  = scrapy.Field()
    About  =  scrapy.Field()
    shipping = scrapy.Field()
    links = scrapy.Field()
    price  = scrapy.Field()
    img_link = scrapy.Field()
