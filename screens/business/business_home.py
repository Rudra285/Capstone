from kivymd.uix.screen import MDScreen
from kivy.uix.scrollview import ScrollView
from kivymd.uix.label import MDLabel
from kivy.properties import StringProperty
from kivymd.uix.card import MDCard
from kivymd.uix.behaviors import RectangularElevationBehavior
from kivy.clock import Clock
from kivymd.uix.dialog import MDDialog
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.button import MDFlatButton
from bigchaindb_driver import BigchainDB
from bigchaindb_driver.crypto import generate_keypair
import os
import json

class CardItem(MDCard, RectangularElevationBehavior):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.elevation = 3
    
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
		self.ids.content.add_widget(CardItem())
    
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
        ##Example of 10 CardItem()'s being created
        #for x in range(10):
         #   self.ids.content.add_widget(CardItem())

        ##TODO figure out how to change the title and subtitle in each cardItem
        ##TODO based on the vehicles being shown. 
        ##TODO example: title = Make, subtitle = Model

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

	def next_one(self):
		self.ids.form.load_next(mode="next")
		self.ids.maint_label.text_color=(76/255, 175/255, 80/255, 1)
		self.ids.progress_one.value = 100
		self.ids.maint_icon.text_color = (76/255, 175/255, 80/255, 1)
		self.ids.maint_icon.icon = "check-decagram"

	def previous(self):
		self.ids.form.load_previous()
		self.ids.customer_label.text_color=(1, 1, 1, 1)
		self.ids.progress_zero.value = 0
		self.ids.customer_icon.icon = "numeric-1-circle"
		self.ids.customer_icon.text_color = (1, 1, 1, 1)


	def previous_one(self):
		self.ids.form.load_previous()
		self.ids.maint_label.text_color = (1, 1, 1, 1)
		self.ids.progress_one.value = 0
		self.ids.maint_icon.icon = "numeric-2-circle"
		self.ids.maint_icon.text_color = (1, 1, 1, 1)







