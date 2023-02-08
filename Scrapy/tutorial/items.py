# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class USCISResponseItem(scrapy.Item):
    # define the fields for your item here like:
    Reciept_Number = scrapy.Field()
    Case_Status = scrapy.Field()
    Description = scrapy.Field()
