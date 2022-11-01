from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty
from kivy.clock import Clock
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDFlatButton
from bigchaindb_driver import BigchainDB
from bigchaindb_driver.crypto import generate_keypair
import os
import requests
from datetime import datetime
from  kivymd.uix.card import MDCardSwipe

class TransferPrompt(MDBoxLayout):
	pass

class CarItem(MDCardSwipe):
	make = StringProperty()
	model = StringProperty()
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
		#print(self.ids.name.text)
		self.dialog.dismiss()

	def maintenance_screen(self, app):
		
		#metadata query car VIN, and get the mainteinance asset
		car_VIN = self.ids.name.tertiary_text
		app.root.get_screen('car_maintenance').load(car_VIN)
		app.root.current = 'car_maintenance'
		

	def transfer(self, fulfilled_creation, current_email, home, *args):
		bdb_root_url = 'https://test.ipdb.io'
		bdb = BigchainDB(bdb_root_url)
		personal_path = os.path.dirname(os.path.abspath("personal.json")) + '/personal.json'
		with open(personal_path, 'r') as p_users:
			personal_users = json.load(p_users)
		p_users.close()
		email = self.dialog.content_cls.ids.recipient.text
		dest = personal_users.get(email)
		recipient_pub = dest[-2]
		business_path = os.path.dirname(os.path.abspath("business.json")) + '/business.json'
		with open(business_path, 'r') as b_users:
			business_users = json.load(b_users)
		b_users.close()
		info = business_users.get(current_email)
		sender_pvt = info[-1]
		
		creation_tx = fulfilled_creation
		if(creation_tx['operation'] == 'CREATE'):
			asset_id = creation_tx['id']
		elif(creation_tx['operation'] == 'TRANSFER'):
			asset_id = creation_tx['asset']['id']
		transfer_asset = {
			'id': asset_id,
		}
		output_index = 0
		output = creation_tx['outputs'][output_index]
		transfer_input = {
			'fulfillment': output['condition']['details'],
			'fulfills': {
				'output_index': output_index,
				'transaction_id': creation_tx['id']
			},
			'owners_before': output['public_keys']
		}
		
		#prepare the transfer of car
		prepared_transfer = bdb.transactions.prepare(
			operation='TRANSFER',
			asset=transfer_asset,
			inputs=transfer_input,
			recipients=recipient_pub,
			metadata = {'owner': recipient_pub}
		)
		
		fulfilled_transfer = bdb.transactions.fulfill(
			prepared_transfer,
			private_keys=sender_pvt,
		)
		
		#send the transfer of the car to joe on the bigchaindb network
		sent_transfer = bdb.transactions.send_commit(fulfilled_transfer)
		
		print("Is " + email + " the owner of the car?", sent_transfer['outputs'][0]['public_keys'][0] == recipient_pub)
		print("Was ford the previous owner of the car?", fulfilled_transfer['inputs'][0]['owners_before'][0] == info[-2])
		print("What is the transaction ID for the transfer from ford to joe?", sent_transfer['id'])
		
		home.remove_widget(self)
		self.dialog.dismiss()
	
    
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
		#mileage = self.ids.create_car_mileage.text
		email = self.ids.email.text
		json_path = os.path.dirname(os.path.abspath("business.json")) + '/business.json'
		with open(json_path, 'r') as b_users:
			user_data = json.load(b_users)
		b_users.close()
		
		info = user_data.get(email)
		recipient_pub = info[-2] #Public key location
		
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
		print(vehicle_asset['data']['vehicle']['make'], vehicle_asset['data']['vehicle']['model'], vehicle_asset['data']['vehicle']['year'], vehicle_asset['data']['vehicle']['VIN'])
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
    	#get the txid of the car creation
		txid_car = fulfilled_creation_tx_car['id']
		print(fulfilled_creation_tx_car)
		print("What is the transaction ID for the creation of the car?", txid_car)
		print("Is ford the owner of the car?", sent_creation_tx_car['outputs'][0]['public_keys'][0] == recipient_pub)
		
		self.add_card(vehicle_asset, fulfilled_creation_tx_car)
    
	def add_card(self, vehicle, fulfilled_creation_tx_car):
		card = CarItem();
		card.ids.name.text = vehicle['data']['vehicle']['make']
		card.ids.name.secondary_text = vehicle['data']['vehicle']['model']
		card.ids.name.tertiary_text = vehicle['data']['vehicle']['VIN']
		card.ids.transfer.on_press=lambda *args: card.transfer_dialog(fulfilled_creation_tx_car, self.ids.name.text, self.ids.content, *args)
		
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
		
		pub = data['Items'][0]['publicKey']
		data_list = bdb.metadata.get(search = pub)
		#print(data_list)
		for i in data_list:
			temp = bdb.transactions.get(asset_id=i['id'])
			#print("FIRST:",temp)
			#print("ALREADY_IN:",already_in)
			if temp[-1]['metadata']['owner'] == pub:
				if temp[-1]['operation'] == 'CREATE':
					vehicle = temp[-1]['asset']
					self.add_card(vehicle, temp[-1])
				elif temp[-1]['operation'] == 'TRANSFER' and (temp[-1]['asset']['id'] not in already_in):
					check = bdb.transactions.get(asset_id=temp[-1]['asset']['id'])
				
					#print("SECOND:", check)
					if(check[-1]['metadata']['owner'] == pub):
						already_in.append(check[-1]['asset']['id'])
						vehicle = check[0]['asset']
						self.add_card(vehicle, temp[-1])
				

	def on_start(self, *args):
		pass

	def clock_next(self, app):
		Clock.schedule_once(self.next)
		
	def logout(self, root, app):
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
		
		temp = bdb.assets.get(search = customer_vin)[0]
		
		info = bdb.transactions.get(asset_id = temp['id'])
		car_key = info[0]['inputs'][0]['owners_before'][0]
		print('car key:', car_key)
		
		json_path = os.path.dirname(os.path.abspath("business.json")) + '/business.json'
		with open(json_path, 'r') as b_users:
			user_data = json.load(b_users)
		b_users.close()
		email = self.ids.name.text
		pub = user_data.get(email)[-2]
		pvt = user_data.get(email)[-1]
		#WHATS INSIDE THE MAINTAINANCE ASSET?
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
		metadata= {'maintenance': maint_data, 'car_vin': customer_vin, 'date': dateStr}
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
		print("What is the transaction ID for the creation of the maintenance?", txid_maintenance)
		
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
		
		print("Is car the owner of maintenance?",
		sent_transfer_tx_maintenance['outputs'][0]['public_keys'][0] == car_key)
		
		print("Was the mechanic shop the previous owner of maintenance?",
		
		fulfilled_transfer_tx_maintenance['inputs'][0]['owners_before'][0] == pub)
		
		print("What is the transaction ID for the transfer from mechanic shop to car?", sent_transfer_tx_maintenance['id'])
