import logging
import os 
import sys
import json


from python_picnic_api import PicnicAPI
from simple_term_menu import TerminalMenu

logging.basicConfig(encoding='utf-8', level=logging.INFO)

logging.warning('Watch out!')

user_name = os.environ.get('USER')
pwd = os.environ.get('PWD')

picnic = PicnicAPI(username=user_name, password=pwd, country_code="NL")
chosen_products = {}

def order_list(list_name):

	with open('./lists/%s' % list_name) as f:
	    lines = f.read().splitlines()

	try:
		with open('./lists/%s.frozen' % list_name, 'r') as frozen:
			chosen_products = json.load(frozen)
	except FileNotFoundError:
		chosen_products = {}

	product_ids = []
	for product in lines:
		if len(product) == 0:
			continue
		logging.info("searching for %s", product)
		result = picnic.search(product)
		logging.debug("result %s", result)
		if len(result) > 0 and len(result[0]["items"]) > 0:
			result_items = result[0]["items"]
			items = ["%s %s %s" % (x["name"], x["unit_quantity"], x["display_price"]) for x in result_items if x["type"] == "SINGLE_ARTICLE"]
			existing_product_id = chosen_products.get(product)
			if existing_product_id is not None:
				logging.info("adding existing product %s, %s" % (product, existing_product_id))
				product_ids.append(existing_product_id)
			else:
				terminal_menu = TerminalMenu(items)
				terminal_choice = terminal_menu.show()
				choice_index = -1 if terminal_choice is None else int(terminal_choice)
				logging.info("choice_index %s", choice_index)
				if choice_index > -1:
					product_choice = result_items[choice_index]
					logging.info("choose %s", product_choice)
					product_id = product_choice["id"]
					chosen_products[product] = product_id
					product_ids.append(product_id)
					logging.info("you choose %s, chosen_products" % product_ids, chosen_products)
		else:
			logging.info("nothing found for %s", product)
	for product_id in product_ids:
		logging.info("adding to cart %s" % product_id)
		picnic.add_product(product_id, count=1)

	logging.info("order is %s" % chosen_products)
	with open('./lists/%s.frozen' % list_name, 'w') as frozen:
		logging.info("freezing order %s" % chosen_products)
		json.dump(chosen_products, frozen)

	logging.info("done")

if __name__ == "__main__":
    print(f"Arguments count: {len(sys.argv)}")
    for i, arg in enumerate(sys.argv):
        print(f"Argument {i:>6}: {arg}")

    order_list(sys.argv[1])