import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import MmidwestoneItem
from itemloaders.processors import TakeFirst
import requests
from scrapy import Selector
pattern = r'(\xa0)?'

url = "https://www.midwestone.bank/modules/blog/ajax/blog-list-items.php"

payload = "ourPage={}&resultsCount=10&URL=&slug="
headers = {
  'authority': 'www.midwestone.bank',
  'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
  'accept': '*/*',
  'x-requested-with': 'XMLHttpRequest',
  'sec-ch-ua-mobile': '?0',
  'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',
  'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
  'origin': 'https://www.midwestone.bank',
  'sec-fetch-site': 'same-origin',
  'sec-fetch-mode': 'cors',
  'sec-fetch-dest': 'empty',
  'referer': 'https://www.midwestone.bank/personal/blog',
  'accept-language': 'en-US,en;q=0.9',
  'cookie': '_ga=GA1.2.441145928.1617627652; _gid=GA1.2.828894226.1617627652; _fbp=fb.1.1617627652598.288928143; monsido=4CE1617627660898; PHPSESSID=8auf0c8makf10u2v6cuabo03c8; _gat_UA-69497746-1=1'
}


class MmidwestoneSpider(scrapy.Spider):
	name = 'midwestone'
	page = 1
	start_urls = ['https://www.midwestone.bank/personal/blog']

	def parse(self, response):
		data = requests.request("POST", url, headers=headers, data=payload.format(self.page))
		links = Selector(text=data.text).xpath('//h3/a/@href').getall()
		yield from response.follow_all(links, self.parse_post)

		if links:
			self.page += 1
			yield response.follow(response.url, self.parse, dont_filter=True)

	def parse_post(self, response):
		date = response.xpath('//span[@class="date"]/text()').get()
		title = response.xpath('//h1/text()').get()
		content = response.xpath('//div[@class="text-content"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=MmidwestoneItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
