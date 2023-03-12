import logging
import os 
import sys
import json


from python_picnic_api import PicnicAPI
from simple_term_menu import TerminalMenu

logging.basicConfig(encoding='utf-8', level=logging.INFO)

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('list')
parser.add_argument('--dry_run', action='store_true', default=False)
args = parser.parse_args()

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

user_name = os.environ.get('USER')
pwd = os.environ.get('PWD')

picnic = PicnicAPI(username=user_name, password=pwd, country_code="NL")
chosen_products = {}

def red(string):
	return "%s %s %s" % (bcolors.FAIL, string, bcolors.ENDC)

def green(string):
	return "%s %s %s" % (bcolors.OKGREEN, string, bcolors.ENDC)

def order_list(list_name, dry_run=True):

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
			existing_product = chosen_products.get(product)
			if existing_product is not None:
				existing_product_id = existing_product["id"]
				existing_product_name = existing_product["name"]
				logging.info("adding existing product %s, %s, %s" % (product, existing_product_id, existing_product_name))
				terminal_menu = TerminalMenu([existing_product_name])
				terminal_choice = terminal_menu.show()
				if terminal_choice != None:
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
					chosen_products[product] = {"id": product_id, "name": items[choice_index]}
					product_ids.append(product_id)
					logging.info("you choose %s, chosen_products" % product_ids, chosen_products)
		else:
			logging.info("%s nothing found for %s %s", bcolors.FAIL, product, bcolors.ENDC)

	if dry_run:
		logging.info("%s dryrun, skipping add to cart%s", bcolors.WARNING, bcolors.ENDC)
	else:
		for product_id in product_ids:
			logging.info("adding to cart %s" % product_id)
			picnic.add_product(product_id, count=1)

		logging.debug(picnic.get_cart())
		cart = picnic.get_cart()
		for main_item in cart["items"]:
			for item in main_item["items"]:
				unavailable_decorators = [d for d in item["decorators"] if d["type"] == "UNAVAILABLE"]
				unavailable = len(unavailable_decorators) > 0
				if unavailable:
					description = unavailable_decorators[0]["explanation"]["short_explanation"]
					logging.warning(red("%s is unavailable: %s" % (item["name"], description)))
				else:
					logging.info(green("%s item added" % item["name"]))

	logging.info("order is %s" % chosen_products)
	with open('./lists/%s.frozen' % list_name, 'w') as frozen:
		logging.info("freezing order %s" % chosen_products)
		json.dump(chosen_products, frozen)

	logging.info("done")

if __name__ == "__main__":
	print(f"Arguments count: {len(sys.argv)}")
	print("args %s, %s" % (args.list, args.dry_run))       
	order_list(args.list, dry_run=args.dry_run)