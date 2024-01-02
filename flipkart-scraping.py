                                                                                               
import json
import csv
from datetime import datetime
import scrapy
import ecom.base

from lxml import etree  # Add this line
from unidecode import unidecode
from ecom.base import BaseSpider
from random import randint
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import TCPTimedOutError
from ui.base import BasePage


class FlipkartSpider(BaseSpider):
    name = 'flipkart'
   # sitemap_urls = ['https://redgorillas.s3.ap-south-1.amazonaws.com/flipkart-dataset/sitemap_v_view-browse.xml']
    sitemap_rules = [('/sports/', 'parse')]
    scraper_category = 'Sports'
    source_name = 'flipkart'
    custom_settings = {
          "CONCURRENT_REQUESTS": 4,
          # "DOWNLOAD_DELAY":,
          "RETRY_TIMES":10

      }
    p_host = 'p.webshare.io:80'
    p_pwd ='dfyybhrzkddf'
    p_user = 'pcfssbxp-'

    def start_requests(self):
        url ='https://redgorillas.s3.ap-south-1.amazonaws.com/flipkart-dataset/sitemap_v_view-browse.xml'
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.7',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Sec-GPC': '1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="118", "Brave";v="118", "Not=A?Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-model': '""',
            'sec-ch-ua-platform': '"Windows"',
            'sec-ch-ua-platform-version': '"15.0.0"',
        }
        yield scrapy.Request(url, callback=self.parse_xml , headers=headers)


    def errors(self,failure):
        with open('errors.csv','a') as f:
            wr = csv.writer(f)
            url = failure.request.url
            date = datetime.today()
            wr.writerow([url,date])

    def parse_xml(self , response):
        root = etree.fromstring(response.body)
        for s in root:
            url = s.getchildren()[0].text
            if '/sports/' in url:
                req =  scrapy.Request(url, callback=self.parse , errback=self.errors)
                proxy = f'http://{self.p_user}{randint(1, 100)}:{self.p_pwd}@{self.p_host}'
                req.meta['proxy'] = proxy
                yield req
            else:
                pass

    def parse(self, response):
        links = response.xpath("//a[contains(@href,'/p/') and @title]/@href").getall()
        for l in links:
            proxy = f'http://{self.p_user}{randint(1, 100)}:{self.p_pwd}@{self.p_host}'
            req = scrapy.Request(response.urljoin(l),callback=self.parse_attr , dont_filter=True , errback=self.errors)
            req.meta['proxy'] = proxy
            yield req

        next_page = response.xpath('//nav/a[last()]/span/text()').get()
        if next_page:
            next_url = response.xpath('//nav/a[last()]/@href').get()
            proxy = f'http://{self.p_user}{randint(1, 100)}:{self.p_pwd}@{self.p_host}'
            req = scrapy.Request(response.urljoin(next_url),callback=self.parse_attr , dont_filter=True , errback=self.errors)
            req.meta['proxy'] = proxy
            yield req


  #  def handle_error(self, failure):
  #      if failure.check(HttpError) and failure.value.response.status == 500:
            # Retry the request with a new proxy
    #        retries = failure.request.meta.get('retry_times', 0)
    #        if retries < 3:  # Retry up to 3 times
    #            request = failure.request.copy()
     #           request.meta['proxy'] = f'http://{self.p_user}{randint(1, 100)}:{self.p_pwd}@{self.p_host}'
     #           request.meta['retry_times'] = retries + 1
    #            return request
    #    # If not a 500 error or reached the maximum retries, log and proceed to the next URL
    #    self.logger.error(f"Failed to fetch {failure.request.url} after 3 retries. Error: {str(failure.value)}")


    def parse_attr(self, response):
        items ={}

        ld_json = response.xpath('//script[@id="jsonLD"]/text()').get()
        try:
            data = json.loads(ld_json)[0]
        except:
            data = None

        json_data = response.xpath("//html").re('__INITIAL_STATE__ = (.*?);</script>')[0]
        try:
            json_init_data = json.loads(json_data)['pageDataV4']['page']['data']['10002'][1]['widget']['data']['pricing']['value']['prices']
        except:
            json_init_data = None

        mrp = None
        offer_price = None
        if json_init_data:
            for price in json_init_data:
                if price['priceType'] =='MRP':
                    mrp = price['decimalValue']
                if price['priceType'] =='SPECIAL_PRICE':
                    offer_price = price['decimalValue']



        items['url'] = response.url
        items['id'] = response.url.split("pid=")[-1].split("&")[0]
        try:
            items['title'] = data['name']
        except:
            items['title'] = response.xpath("//h1/span/text()").get()

        try:
            items['offer_price'] = data['offers']['price']
        except:
            items['offer_price'] = response.xpath('//div[@class="_19_Y9G _8XxizX"]/text()').get('').strip(",").strip("₹").strip()

        if items['offer_price'] is None or items['offer_price'] =='':
            items['offer_price'] = response.xpath('//div[@class="_19_Y9G _8XxizX"]/text()').get('').strip(",").strip("₹").strip()

        if items['offer_price'] is None or items['offer_price'] =='':
            items['offer_price'] = response.xpath('//div[contains(text(),"Selling Price")]/following-sibling::div/text()').get('').strip(",").strip("₹").strip()

        if items['offer_price'] is None or items['offer_price']=='':
            items['offer_price'] = response.xpath('//div[@class="aMaAEs"]//div[contains(text(),"₹")]/text()').get('').strip(",").strip("₹").strip()

        items['mrp'] = response.xpath('//div[contains(text(),"Maximum Retail Price")]/following-sibling::div/text()').get('').strip(",").strip("₹").strip()

        try:
            mrp2 = response.xpath('//div[@class="aMaAEs"]//div[contains(text(),"₹")]/text()').getall()[-1]
        except:
            mrp2 = None

        if items['mrp'] is None or items['mrp'] =='':
            items['mrp'] = mrp2
        if items['mrp']:
            items['mrp'] = items['mrp'].replace(",","").replace("₹","").strip()

        try:
            items['brand'] = data['brand']['name']
        except:
            items['brand'] = response.xpath('//*[@class="_3dtsli"]//td[contains(text(),"Brand")]/following::li[1]/text()').get()

        items['model'] = response.xpath('//*[@class="_3dtsli"]//td[contains(text(),"Model")]/following::li[1]/text()').get()
        items['style'] = None
        items['color'] = None
        try:
            items['sport_type'] = json.loads(json_data)['pageDataV4']['page']['pageData']['pageContext']['analyticsData']['subCategory']
        except:
            items['sport_type'] = None
        items['material'] = None
        items['weight'] = None
        items['height'] = None
        items['description'] = response.xpath('//div[@class="_1mXcCf RmoJUa"]/text()').get()
        try:
            items['image'] = data['image']
        except:
            items['image'] = response.xpath("//img[@loading='eager']/@src").get()

        # if items['mrp'] is None or items['mrp'] =='':
        #     items['mrp'] = mrp
        if items['offer_price'] is None or  items['offer_price'] =='':
            items['offer_price'] = offer_price

        if items['offer_price']:
            items['offer_price'] = str(items['offer_price']).replace(",","").strip()
        
        attr_lst =[]
        attr_tbl = response.xpath('//*[@class="_3dtsli"]//table')
        for tbl in attr_tbl:
            trs = tbl.xpath(".//tr")
            for tr in trs:
                attr_title = tr.xpath('.//td/text()').get()
                attr_value = tr.xpath(".//td[2]//li/text()").get()
                if attr_title and len(attr_title)>0:
                    d ={attr_title:attr_value}
                    attr_lst.append(d)
                    # print(f'{attr_title}-{attr_value}')
        items['product_attributes'] = attr_lst
        for attr in attr_lst:
            for key , val in attr.items():
                if 'style' in key.lower():
                    items['style'] =val
                if 'color' in key.lower():
                    items['color'] =val
                if 'material' in key.lower():
                    items['material'] =val
                if 'weight' in key.lower():
                    items['weight'] =val
                if 'height' in key.lower():
                    items['height'] =val
                if 'brand' in key.lower():
                    items['brand'] =val
        items['tags'] = None

        if items['id']:
            yield items
        
