from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty
from kivy.clock import Clock
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDFlatButton
from bigchaindb_driver import BigchainDB
from bigchaindb_driver.crypto import generate_keypair
from bigchaindb_driver.common.crypto import PrivateKey
import os
import requests
from datetime import datetime
from  kivymd.uix.card import MDCardSwipe
from screens.escrow import Escrow
from multiprocessing import Process

class TransferPrompt(MDBoxLayout):
	pass

class CarItem(MDCardSwipe):
	make = StringProperty()
	model = StringProperty()
	screen = ''
	scrollview = None
	dialog = None

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.elevation = 3
	
	def transfer_dialog(self, fulfilled_creation_tx_car, current_email, home, *args):
		if not self.dialog:
			self.dialog = MDDialog(
                title="Transfer Vehicle:",
                type="custom",
                content_cls=TransferPrompt(),
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        on_press = self.close_carlog
                    ),
                    MDFlatButton(
                        text="SUBMIT",
                        on_press = lambda *args: self.transfer(fulfilled_creation_tx_car, current_email, home, *args)
                    ),
                ],
            )
		self.dialog.open()
		
	def close_carlog(self, obj):
		self.dialog.content_cls.ids.transfer_alert.text = ''
		self.dialog.content_cls.ids.key.text = ''
		self.dialog.content_cls.ids.recipient.text = ''
		self.dialog.dismiss()

	def maintenance_screen(self, app):
		
		#metadata query car VIN, and get the mainteinance asset
		car_VIN = self.ids.name.tertiary_text
		app.root.get_screen('car_maintenance').load(car_VIN, self.screen)
		self.scrollview.clear_widgets()
		app.root.current = 'car_maintenance'
		

	def transfer(self, fulfilled_creation, current_email, home, *args):
		sender_pvt = self.dialog.content_cls.ids.key.text
		email_str = self.dialog.content_cls.ids.recipient.text
		
		if sender_pvt != '' and email_str != '':
			bdb_root_url = 'https://test.ipdb.io'
			bdb = BigchainDB(bdb_root_url)
			URL = "https://1r6m03cirj.execute-api.us-west-2.amazonaws.com/test/users"
			email_list = email_str.split()
			recipient_public = []
			for i in email_list:
				user = requests.get(url = URL, params = {'email': i})
				dest_data = user.json()
				if len(dest_data['Items']) != 0:
					recipient_pub = dest_data['Items'][0]["publicKey"]["S"]
					recipient_public.append(recipient_pub)
				else:
					self.dialog.content_cls.ids.transfer_alert.text = 'Account ' + i + ' was not found'
			if len(recipient_public) != 0:
				recipient_public_tup = tuple(recipient_public)
				
				owner_public_keys = fulfilled_creation['outputs'][0]['public_keys']
				
				Process(target = Escrow.verify, args=(Escrow, sender_pvt, owner_public_keys, recipient_public_tup, recipient_public, home, self, fulfilled_creation)).start()
				
				self.dialog.content_cls.ids.transfer_alert.text = ''
				self.dialog.dismiss()
			
			self.dialog.content_cls.ids.key.text = ''
			self.dialog.content_cls.ids.recipient.text = ''
		else:
			self.dialog.content_cls.ids.transfer_alert.text = 'Fill in all the fields'
			
class BusinessHomeScreen(MDScreen):

	make_prompt = StringProperty("Make")
	model_prompt = StringProperty("Model")
	year_prompt = StringProperty("Year")
	vin_prompt = StringProperty("VIN")
	mileage_prompt = StringProperty("Mileage")

	make = StringProperty()
	model = StringProperty()
	year = StringProperty()
	vin = StringProperty()
	mileage = StringProperty()

	submit = StringProperty("Submit button pressed")

	def __init__(self, **kwargs):
		super(BusinessHomeScreen, self).__init__(**kwargs)
		Clock.schedule_once(self.on_start)

	def onCreateVehicleClick(self):
		car_key = generate_keypair()
		bdb_root_url = 'https://test.ipdb.io'
		bdb = BigchainDB(bdb_root_url)

		make = self.ids.create_car_make.text
		model = self.ids.create_car_model.text
		year = self.ids.create_car_year.text
		vin = self.ids.create_car_vin.text
		if make != '' and model != '' and year != '' and vin != '':
			email = self.ids.email.text
			URL = "https://1r6m03cirj.execute-api.us-west-2.amazonaws.com/test/users"
			vin_check = bdb.assets.get(search = vin)
			if len(vin_check) == 0:
				self.ids.creation_alert.text = ''
				self.ids.create_car_make.text = ''
				self.ids.create_car_model.text = ''
				self.ids.create_car_year.text = ''
				self.ids.create_car_vin.text = ''
				user = requests.get(url = URL, params = {'email': email})
				data = user.json()
				recipient_pub = data['Items'][0]["publicKey"]["S"]
				
				#Make a car asset that is brand new
				vehicle_asset = {
					'data': {
						'vehicle': {
							'make': make,
							'VIN': vin,
							'model': model,
							'year': year,
							'mileage': '0km',
						}
					}
				}
				
				prepared_creation_tx_car = bdb.transactions.prepare(
					operation='CREATE',
					signers=car_key.public_key,
					recipients=(recipient_pub),
					asset=vehicle_asset,
					metadata= {'owner': recipient_pub}
				)
				
				#fulfill the creation of the car by signing with the cars private key
				fulfilled_creation_tx_car = bdb.transactions.fulfill(
					prepared_creation_tx_car,
					private_keys=car_key.private_key
				)
				
				#send the creation of the car to bigchaindb
				sent_creation_tx_car = bdb.transactions.send_commit(fulfilled_creation_tx_car)
				
				self.add_card(vehicle_asset, fulfilled_creation_tx_car)
			
			else:
				self.ids.creation_alert.text = 'VIN already exists'
				self.ids.create_car_vin.text = ''
		else:
			self.ids.creation_alert.text = 'Fill in all the fields'
    
	def add_card(self, vehicle, fulfilled_creation_tx_car):
		card = CarItem();
		card.screen = self.name
		card.scrollview = self.ids.content
		card.ids.name.text = vehicle['data']['vehicle']['make']
		card.ids.name.secondary_text = vehicle['data']['vehicle']['model']
		card.ids.name.tertiary_text = vehicle['data']['vehicle']['VIN']
		card.ids.transfer.on_press=lambda *args: card.transfer_dialog(fulfilled_creation_tx_car, self.ids.email.text, self.ids.content, *args)
		
		self.ids.content.add_widget(card)
    
	def load(self):
		already_in = []
		
    		#Load all vehicles owned by the business
		bdb_root_url = 'https://test.ipdb.io'
		bdb = BigchainDB(bdb_root_url)
		URL = "https://1r6m03cirj.execute-api.us-west-2.amazonaws.com/test/users"
		
		email = self.ids.email.text
		user = requests.get(url = URL, params = {'email': email})
		data = user.json()
		self.ids.account_name.title = data['Items'][0]['name']['S']
		pub = data['Items'][0]['publicKey']["S"]
		data_list = bdb.metadata.get(search = pub)

		for i in data_list:
			temp = bdb.transactions.get(asset_id=i['id'])

			if pub in temp[-1]['metadata']['owner']:
				if temp[-1]['operation'] == 'CREATE':
					vehicle = temp[-1]['asset']
					self.add_card(vehicle, temp[-1])
				elif temp[-1]['operation'] == 'TRANSFER' and (temp[-1]['asset']['id'] not in already_in):
					check = bdb.transactions.get(asset_id=temp[-1]['asset']['id'])
				
					
					if(pub in check[-1]['metadata']['owner']):
						already_in.append(check[-1]['asset']['id'])
						vehicle = check[0]['asset']
						self.add_card(vehicle, temp[-1])
				

	def on_start(self, *args):
		pass

	def clock_next(self, app):
		Clock.schedule_once(self.next)
		
	def logout(self, root, app):
		self.ids.content.clear_widgets()
		app.root.current = 'startup_screen'
    	
	def next(self):
		self.ids.form.load_next(mode="next")
		self.ids.customer_label.text_color=(76/255, 175/255, 80/255, 1)
		self.ids.progress_zero.value = 100
		self.ids.customer_icon.text_color = (76/255, 175/255, 80/255, 1)
		self.ids.customer_icon.icon = "check-decagram"

	def previous(self):
		self.ids.form.load_previous()
		self.ids.customer_label.text_color=(1, 1, 1, 1)
		self.ids.progress_zero.value = 0
		self.ids.customer_icon.icon = "numeric-1-circle"
		self.ids.customer_icon.text_color = (1, 1, 1, 1)
	
	def submit(self):
		bdb_root_url = 'https://test.ipdb.io'  # Use YOUR BigchainDB Root URL here
		bdb = BigchainDB(bdb_root_url)
		
		#Get date and time for maintenance creation
		dateTimeObj = datetime.now()
		month = str(dateTimeObj.month)
		day =  str(dateTimeObj.day)
		year = str(dateTimeObj.year)
		hour = str(dateTimeObj.hour)
		minute = str(dateTimeObj.minute)
		seconds = str(dateTimeObj.second)
		if(dateTimeObj.second < 10):
			seconds = '0' + str(dateTimeObj.second)
		if(dateTimeObj.minute < 10):
			minute = '0' + str(dateTimeObj.minute)
		if(dateTimeObj.hour > 12):
			hour = str(dateTimeObj.hour - 12)
		if(dateTimeObj.hour >= 12):
			dateStr = month + '/' + day + '/' + year + '\n' + hour + ':' + minute + ':' + seconds + ' PM'
		else:
			dateStr = month + '/' + day + '/' + year + '\n' + hour + ':' + minute + ':' + seconds + ' AM'
		
		customer_vin = self.ids.vin.text
		customer_mileage = self.ids.mileage.text
		maint_data = self.ids.maint_performed.text
		pvt = self.ids.user_key.text
		if pvt != '' and customer_vin != '' and maint_data != '':
			temp = bdb.assets.get(search = customer_vin)
			
			URL = "https://1r6m03cirj.execute-api.us-west-2.amazonaws.com/test/users"
			
			email = self.ids.email.text
			company = self.ids.account_name.title
			user = requests.get(url = URL, params = {'email': email})
			data = user.json()
			
			pub = data['Items'][0]['publicKey']["S"]
			try:
				encrypt_pvt = PrivateKey(pvt)
				decrypted_pub = encrypt_pvt.get_verifying_key().encode().decode()
				if decrypted_pub == pub:
					valid_key = True
				else:
					valid_key = False
			except:
				valid_key = False
				
			if len(temp) != 0 and valid_key:
				temp = temp[0]
				info = bdb.transactions.get(asset_id = temp['id'])
				car_key = info[0]['inputs'][0]['owners_before'][0]
				
				
				
				#TODO:WHATS INSIDE THE MAINTAINANCE ASSET?
				maintenance_asset = {
					'data': {
						'vehicle': {
							'business': 'Ford',
							'model': 'MKX',
							'year': '2008',
							'VIN': customer_vin,
							'Mileage': '1,000km',
						}
					}
				}
				
				#Prepare the creation of the maintenance owned by the mechanic shop
				prepared_creation_tx_maintenance = bdb.transactions.prepare(
					operation='CREATE',
					signers=pub,
					#asset=maintenance_asset,
					metadata= {'maintenance': maint_data, 'car_vin': customer_vin, 'date': dateStr, 'company': company}
				)
				
				#fulfill the creation of the maintenance owned by the mechanic shop
				fulfilled_creation_tx_maintenance = bdb.transactions.fulfill(
					prepared_creation_tx_maintenance,
					private_keys=pvt
				)
				
				#send the creation of the maintenance to bigchaindb
				sent_creation_tx_maintenance = bdb.transactions.send_commit(fulfilled_creation_tx_maintenance)
				
				#get the txid of the maintenance creation
				txid_maintenance = fulfilled_creation_tx_maintenance['id']
				
				creation_tx_maintenance = fulfilled_creation_tx_maintenance
				
				asset_id_maintenance = creation_tx_maintenance['id']
				
				transfer_asset_maintenance = {
					'id': asset_id_maintenance,
				}
				
				output_index = 0
				output = creation_tx_maintenance['outputs'][output_index]
				
				transfer_input_maintenance = {
					'fulfillment': output['condition']['details'],
					'fulfills': {
						'output_index': output_index,
						'transaction_id': creation_tx_maintenance['id']
					},
					'owners_before': output['public_keys']
				}
				
				prepared_transfer_tx_maintenance = bdb.transactions.prepare(
					operation='TRANSFER',
					asset=transfer_asset_maintenance,
					inputs=transfer_input_maintenance,
					recipients=car_key,
				)
				
				fulfilled_transfer_tx_maintenance = bdb.transactions.fulfill(
					prepared_transfer_tx_maintenance,
					private_keys=pvt,
				)
				
				sent_transfer_tx_maintenance = bdb.transactions.send_commit(fulfilled_transfer_tx_maintenance)
				self.ids.maint_alert.text = ''
				self.ids.vin.text = ''
				self.ids.maint_performed.text = ''
				self.ids.user_key.text = ''
			else:
				self.ids.maint_alert.text = 'Incorrect Vin or Private Key'
				self.ids.vin.text = ''
				self.ids.user_key.text = ''
		else:
			self.ids.maint_alert.text = 'Fill in all the fields'
