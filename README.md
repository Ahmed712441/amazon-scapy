# amazon-scapy
Full Api for scraping amazon</br></br>
This Api can pypass captcha </br>
Extracts price,shipping,tittle ,feauters,Description,img_link,link of items of your choosen search key</br></br>
## if you want to extrat file as .csv
```
# search_key the items in which you want to search
# number_of_pages which you want to scrape
# table the table name in database (if not exits it will be created with this name)
scrapy crawl amazon -a search_key=headphones -a number_of_pages=10 -s table= "headphones" -o name_of_csv_file.csv
```
</br>

## if you want to extrat file as .xml
```
scrapy crawl amazon -a search_key=headphones -a number_of_pages=10 -s table= "headphones" -o name_of_xml_file.xml
```

</br>

## if you want to extrat file as .json
```
scrapy crawl amazon -a search_key=headphones -a number_of_pages=10 -s table= "headphones" -o name_of_json_file.json
```
</br>

## by default it is saved to the database

</br></br>
## Requirments
```
opencv
Tensorflow (for using the model that is created for solving captcha)
scrapy
numpy
```
</br>

## you need to install the captcha_solver model and provide the path for it in your device 
give the path for captcha.json in amazon_spider at line 16</br>
give the path for captcha.h5 in amazon_spider at line 20
