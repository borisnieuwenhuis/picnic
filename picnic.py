import logging
import os 

from python_picnic_api import PicnicAPI
from simple_term_menu import TerminalMenu

logging.basicConfig(encoding='utf-8', level=logging.INFO)

logging.warning('Watch out!')

user_name = os.environ.get('USER')
pwd = os.environ.get('PWD')

picnic = PicnicAPI(username=user_name, password=pwd, country_code="NL")

result = picnic.get_cart()


list_name = "ayurvada"

with open('./lists/%s' % list_name) as f:
    lines = f.read().splitlines()

# print(lines)


product_ids = []
for product in lines:
	logging.info("searching for %s", product)
	result = picnic.search(product)
	result_items = result[0]["items"]
	items = ["%s %s %s" % (x["name"], x["unit_quantity"], x["display_price"]) for x in result_items if x["type"] == "SINGLE_ARTICLE"]
	terminal_menu = TerminalMenu(items)
	choice_index = int(terminal_menu.show())
	product_choice = result_items[choice_index]
	logging.info("choose %s", product_choice)
	product_id = product_choice["id"]
	product_ids.append(product_id)

logging.info("you choose %s" % product_ids)

for product_id in product_ids:
	logging.info("adding to cart %s" % product_id)
	picnic.add_product(product_id, count=1)

