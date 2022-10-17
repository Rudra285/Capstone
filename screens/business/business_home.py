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
import json
from  kivymd.uix.card import MDCardSwipe

class TransferPrompt(MDBoxLayout):
	pass
class CarItem(MDCardSwipe):

	##TODO connect the make/model variables to the make/model of the car being created
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
	def transfer(self, fulfilled_creation, current_email, home, *args):
		car_key = generate_keypair()
		bdb_root_url = 'https://test.ipdb.io'  # Use YOUR BigchainDB Root URL here
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
		asset_id = creation_tx['id']
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
		
		#prepare the transfer of car to joe
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

		print("Create Car Button Clicked")
		car_key = generate_keypair()
		bdb_root_url = 'https://test.ipdb.io'  # Use YOUR BigchainDB Root URL here
		bdb = BigchainDB(bdb_root_url)

		make = self.ids.create_car_make.text
		print(make)
		model = self.ids.create_car_model.text
		print(model)
		year = self.ids.create_car_year.text
		print(year)
		vin = self.ids.create_car_vin.text
		print(vin)
		#mileage = self.ids.create_car_mileage.text
		#print(mileage)
		print(self.ids.name.text)
		email = self.ids.name.text
		json_path = os.path.dirname(os.path.abspath("business.json")) + '/business.json'
		with open(json_path, 'r') as b_users:
			user_data = json.load(b_users)
		b_users.close()
		
		info = user_data.get(email)
		print(info)
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
		card.ids.transfer.on_press=lambda *args: card.transfer_dialog(fulfilled_creation_tx_car, self.ids.name.text, self.ids.content, *args)
		
		self.ids.content.add_widget(card)
    
	def load(self):
    	#Load all vehicles owned by the business
		bdb_root_url = 'https://test.ipdb.io'  # Use YOUR BigchainDB Root URL here
		bdb = BigchainDB(bdb_root_url)
		json_path = os.path.dirname(os.path.abspath("business.json")) + '/business.json'
		with open(json_path, 'r') as b_users:
			user_data = json.load(b_users)
		b_users.close()
		email = self.ids.name.text
		pub = user_data.get(email)[-2]
		data_list = bdb.metadata.get(search = pub)
		print(data_list)
		for i in data_list:
			temp = bdb.transactions.get(asset_id=i['id'])
			print(temp)
			check = temp[-1]['metadata']
			check['owner'] == pub
			if temp[-1]['operation'] == 'CREATE':
				vehicle = temp[-1]['asset']
				self.add_card(vehicle, temp[-1])	

	def on_start(self, *args):
		pass

        #TODO IF any cars are owned determine how many, put that in a variable
        ##Example of 10 CarItem()'s being created
		

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
		
		customer_vin = self.ids.vin.text
		print(customer_vin)
		customer_mileage = self.ids.mileage.text
		print(customer_mileage)
		maint_data = self.ids.maint_performed.text
		print(maint_data)
		
		temp = bdb.assets.get(search = customer_vin)[0]
		print(temp)
		
		info = bdb.transactions.get(asset_id = temp['id'])
		car_key = info[0]['inputs'][0]['owners_before'][0]
		print(car_key)
		
		#TODO-need to find a way to retrieve maintainence
		maintenance_asset = {
			'data': {
				'vehicle': {
					'make': 'Lincoln',
					'model': 'MKX',
					'year': '2008',
					'VIN': 'SUV',
					'Mileage': '1,000km',
				}
			}
		}
