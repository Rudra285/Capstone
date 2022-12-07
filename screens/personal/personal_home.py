from kivymd.uix.screen import MDScreen
from kivy.clock import Clock
import os
import requests
from kivymd.uix.dialog import MDDialog
from kivy.properties import StringProperty
from  kivymd.uix.card import MDCardSwipe
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import IRightBodyTouch
from kivymd.uix.button import MDFlatButton
from bigchaindb_driver import BigchainDB
from screens.escrow import Escrow
from multiprocessing import Process

class TransferPersonalPrompt(MDBoxLayout):
	pass

class CarItemPersonal(MDCardSwipe):
	make = StringProperty()
	model = StringProperty()
	screen = ''
	scrollview = None
	dialog = None

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.elevation = 3
	
	def transfer_dialog(self, fulfilled_tx_car, current_email, home, *args):
		
		#Show a transfer pop dialog
		if not self.dialog:
			self.dialog = MDDialog(
                title="Transfer Vehicle",
                type="custom",
                content_cls=TransferPersonalPrompt(),
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        on_press = self.close_carlog
                    ),
                    MDFlatButton(
                        text="SUBMIT",
                        on_press = lambda *args: self.transfer_personal(fulfilled_tx_car, current_email, home, *args)
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
		
		#Go to vehicle history
		car_VIN = self.ids.name_personal.tertiary_text
		app.root.get_screen('car_maintenance').load(car_VIN, self.screen)
		self.scrollview.clear_widgets()
		app.root.current = 'car_maintenance'
	
	def remove_card(self):
		self.scrollview.remove_widget(self) #Remove vehicle card after transfer
	
	def transfer_personal(self, fulfilled_creation, current_email, home, *args):
		sender_pvt = self.dialog.content_cls.ids.key.text
		email_str = self.dialog.content_cls.ids.recipient.text
		
		#Error check for empty fields
		if sender_pvt != '' and email_str != '':
			
			#Establish connection to BigChainDB
			bdb_root_url = 'https://test.ipdb.io'
			bdb = BigchainDB(bdb_root_url)
			
			URL = "https://1r6m03cirj.execute-api.us-west-2.amazonaws.com/test/users" #For GET request
			email_list = email_str.split() #Splt the recipent emails into list
			recipient_public = []
			recipient_names = []
			
			#Send GET request for every email
			for i in email_list:
				user = requests.get(url = URL, params = {'email': i})
				dest_data = user.json()
				
				#If account was found in the database
				if len(dest_data['Items']) != 0:
					recipient_pub = dest_data['Items'][0]["publicKey"]["S"]
					dest_name = dest_data['Items'][0]["name"]["S"]
					recipient_public.append(recipient_pub)
					recipient_names.append(dest_name)
				else:
					self.dialog.content_cls.ids.transfer_alert.text = 'Account ' + i + ' was not found'
			
			#If any recipients found in database
			if len(recipient_public) != 0:
				#Initialize variables
				recipient_public_tup = tuple(recipient_public)
				owner_public_keys = fulfilled_creation['outputs'][0]['public_keys']
				car_VIN = self.ids.name_personal.tertiary_text
				
				#Start process to transfer vehicle
				Process(target = Escrow.verify, args=(Escrow, sender_pvt, owner_public_keys, recipient_public_tup, recipient_public, self, fulfilled_creation, recipient_names, car_VIN)).start()
				
				self.dialog.content_cls.ids.transfer_alert.text = ''
				self.dialog.dismiss()
			
			self.dialog.content_cls.ids.key.text = ''
			self.dialog.content_cls.ids.recipient.text = ''
		else:
			self.dialog.content_cls.ids.transfer_alert.text = 'Fill in all the fields'

class PersonalHomeScreen(MDScreen):

	def __init__(self, **kwargs):
		super(PersonalHomeScreen, self).__init__(**kwargs)
		Clock.schedule_once(self.on_start)
        
	def add_card(self, vehicle, fulfilled_tx_car):
		card = CarItemPersonal();
		
		#Set card data
		card.screen = self.name
		card.scrollview = self.ids.content_personal
		card.ids.name_personal.text = vehicle['data']['vehicle']['make']
		card.ids.name_personal.secondary_text = vehicle['data']['vehicle']['model']
		card.ids.name_personal.tertiary_text = vehicle['data']['vehicle']['VIN']
		card.ids.transfer_personal.on_press=lambda *args: card.transfer_dialog(fulfilled_tx_car, self.ids.email.text, self.ids.content_personal, *args)
    	
		self.ids.content_personal.add_widget(card)
        
	def load(self):
		already_in = []
		
		#Establish connection to BigChainDB
		bdb_root_url = 'https://test.ipdb.io'
		bdb = BigchainDB(bdb_root_url)
		
		#Send GET request to database
		email = self.ids.email.text
		URL = "https://1r6m03cirj.execute-api.us-west-2.amazonaws.com/test/users"
		user = requests.get(url = URL, params = {'email': email})
		data = user.json()
		self.ids.account_name.title = data['Items'][0]['name']['S']
		pub = data['Items'][0]['publicKey']["S"]
		
		data_list = bdb.metadata.get(search = pub) #Query BigchainDB for public key of user in metadata
		
		#Load all vehicles which have the public key in metadata
		for i in data_list:
			temp = bdb.transactions.get(asset_id=i['id'])
    		
			if temp[-1]['operation'] == 'TRANSFER' and (temp[-1]['asset']['id'] not in already_in):
				check = bdb.transactions.get(asset_id=temp[-1]['asset']['id'])
				if(pub in check[-1]['metadata']['owner_key']):
					already_in.append(check[-1]['asset']['id'])
					vehicle = check[0]['asset']
					self.add_card(vehicle, temp[-1])	

	def on_start(self, *args):
		pass

	def logout(self, root, app):
		self.ids.content_personal.clear_widgets()
		app.root.current = 'startup_screen'

	def clock_next(self, app):
		Clock.schedule_once(self.next)
