import taxjar

import os

from pizzapi import Customer
from pizzapi import Address
from pizzapi import Order
from pizzapi import Menu
from pizzapi import PaymentObject

tax_api_key = '---'

def getTax(zipcode):
	taxClient = taxjar.Client(api_key=tax_api_key)
	return taxClient.rates_for_location(zipcode).city_rate

def welcome():
	print('Welcome to the Super Duper Dominos Pizza Terminal Experience.')
	print('To begin, start by typing in your delivery info.\n')

def getCustomerAndAddress():
	firstName = input('First name: ')
	lastName = input('Last name: ')

	email = input('Email: ')
	phone = input('Phone #: ')

	streetAddr = input('Street address: ')
	city = input('City: ')
	state = input('State: ')
	zipcode = input('Zipcode: ')

	addr = streetAddr + ',' + city + ',' + state + ',' + zipcode

	customer = Customer(firstName, lastName, email, phone, addr)
	address = Address(streetAddr, city, state, zipcode)

	return customer, address

def findStore(address):
	print('\n')
	print('Locating nearest store')
	store = address.closest_store()
	print('Nearest store is located at:\n')

	store_data = store.get_details()
	print(store_data['StreetName'])
	print(store_data['City'])
	print(store_data['Region'])
	print(store_data['PostalCode'])

	return store

def instructions():
	print('\nTo add items to your basket, type \'\033[1;33;40madd\033[1;37;40m\' and then the item code and the quantity.')
	print('To remove items from your basket, type \'\033[1;33;40mremove\033[1;37;40m\' and the item code.')
	print('To view your basket, type \'\033[1;33;40mbasket\033[1;37;40m\'.')
	print('To search to the menu for an item code based on a keyword, type \'\033[1;33;40msearch\033[1;37;40m\' and then the keyword.')
	print('To see the menu for the selected store, type \'\033[1;33;40mmenu\033[1;37;40m\'.')
	print('To finalize your order and checkout, type \'\033[1;33;40mcheckout\033[1;37;40m\'.')
	print('To cancel your order, type \'\033[1;33;40mcancel\033[1;37;40m\'.\n')

def addItem(order, tokens, menu):
	code = str(tokens[1]).upper()
	qty = 1

	if(len(tokens) > 2):
		qty = tokens[2]
		try:
			qty = int(qty)
		except ValueError:
			print("Specified quantity was not an integer.")
			return False
	try:
		for i in range(0, qty):
			order.add_item(code)
	except KeyError:
		print("Invalid item code.")
		return False

	return True

def removeItem(order, tokens):
	code = tokens[1].upper()

	try:
		order.remove_item(code)
	except:
		print("Invalid item code.")
		return False

	return True

def search_menu(order, tokens, menu):
	if(len(tokens) < 2):
		print('Please specify search criteria.')
		return

	items = menu.variants.values()

	hits = {}

	for item in items:
		name = item['Name']

		if tokens[1].lower() in name.lower():
			hits.update({item['Code']: item})


	for h in hits:
		print(hits[h]['Code'] + "\t\t\t" + hits[h]['Name'] + "\t\t\t$" + hits[h]['Price'])

def getBasket(order):
	total = 0.0

	items = order.data['Products']
	if(len(items) == 0):
		print('There is nothing in your basket.')
	for i in items:
		print(i['Name'] + "\t\t$" + i['Price'])
		total += float(i['Price'])
	if(total != 0.0):
		print('Total: ' + str(total))

	return total

def getOrder(store, customer, address):
	inp = ''

	order = Order(store, customer, address)
	menu = order.menu

	while inp != 'checkout':

		inp = input(': ')

		tokens = inp.split(' ')

		inp = tokens[0].lower()

		command = tokens[0]
		if(command == 'add'):

			if(len(tokens) < 2):
				print("Please specify item code.")
				continue

			added = addItem(order, tokens, menu)

			if not added:
				print("Failed to add item to order.")
			else:
				print("Item added to order.")

		elif(command == 'remove'):
			if(len(tokens) < 2):
				print("Please specify item code.")
				continue

			removed = removeItem(order, tokens)

			if not removed:
				print("Failed to remove item from basket.")
			else:
				print("Item successfully removed")

		elif(command == 'basket'):
			getBasket(order)

		elif(command == 'menu'):

			varis = menu.variants.values()
			for v in varis:
				c = v['Code']
				n = v['Name']
				p = v['Price']
				print(c + "\t\t\t" + n + "\t\t\t$" + p)

		elif(command == 'cancel'):
			return False

		elif(command == 'search'):
			search_menu(order, tokens, menu)

		else:
			print("Invalid command.")

	
	return order

def checkout_order(order):
	card_number = input("Credit card number: ")
	expire = input("Expiration date (mm/yy): ")
	cvv = input("CVV: ")
	z = input("ZIP code: ")

	payment = PaymentObject(card_number, expire, cvv, z)

	print('Placing order...')
	order.place(payment)
	print('Order has been placed! Enjoy :)')

def main():
	os.system('cls' if os.name == 'nt' else 'clear')

	welcome()

	customer, address = getCustomerAndAddress()

	store = findStore(address)

	instructions()

	order = getOrder(store, customer, address)

	if not order:
		print("peace yo.")
	else:
		total = getBasket(order)
		print('Estimated total with tax: ' + str(total + total * float(getTax(address.zip))))
		i = input('\nIs this the correct order (Y/N).')
		if(i.lower() == 'y'):
			checkout_order(order)
		else:
			print("Please type \'\033[1;33;40mcancel\033[1;37;40m\' to cancel your order and start again.")

main()