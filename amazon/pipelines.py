# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import sqlite3

class AmazonPipeline:

    @classmethod
    def from_crawler(cls, crawler):
        # Here, you get whatever value was passed through the "table" parameter
        settings = crawler.settings
        table = settings.get('table')
        # print("table" + table)

        # Instantiate the pipeline with your table
        return cls(table)

    def __init__(self,table):
        self.table = table
        self.connect()
        self.create_table()


    def process_item(self, item, spider):

        self.add_item(item)
        # print(item)
        return item

    def connect(self):

        self.conn = sqlite3.connect('amazon.db')
        self.curr = self.conn.cursor()

    def add_item(self,item):
        String = """
        insert into {} values
        (?,?,?,?,?,?,?)
        """.format(self.table)
        # print(String)
        self.curr.execute(String,(item['title'],item['feauture'],item['About'],item['price'],item['shipping'],item['links'],item['img_link']))

        self.conn.commit()

    def create_table(self):
        string = f'create table IF NOT EXISTS {self.table} (title text,feauture text,About text,price float,shipping float,links text,img_link text);'
        self.curr.execute(string)
        self.conn.commit()
