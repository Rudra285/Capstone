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

class EscrowNotificationPrompt(MDBoxLayout):
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
		if not self.dialog:
			self.dialog = MDDialog(
                title="Transfer Vehicle:",
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
		self.dialog.dismiss()

	def maintenance_screen(self, app):
    	#metadata query car VIN, and get the mainteinance asset
		car_VIN = self.ids.name_personal.tertiary_text
		app.root.get_screen('car_maintenance').load(car_VIN, self.screen)
		self.scrollview.clear_widgets()
		app.root.current = 'car_maintenance'
    
	def transfer_personal(self, fulfilled_creation, current_email, home, *args):
		bdb_root_url = 'https://test.ipdb.io'
		bdb = BigchainDB(bdb_root_url)
		URL = "https://1r6m03cirj.execute-api.us-west-2.amazonaws.com/test/users"
		email_str = self.dialog.content_cls.ids.recipient.text#Subject to change
		email_list = email_str.split() #Subject to change
		recipient_public = []
		for i in email_list:
			user = requests.get(url = URL, params = {'email': i})
			dest_data = user.json()
			
			recipient_pub = dest_data['Items'][0]["publicKey"]["S"]
			recipient_public.append(recipient_pub)
		
		recipient_public_tup = tuple(recipient_public)
		
		sender_pvt = self.dialog.content_cls.ids.key.text
		owner_public_keys = fulfilled_creation['outputs'][0]['public_keys']
		
		Process(target = Escrow.verify, args=(Escrow, sender_pvt, owner_public_keys, recipient_public_tup, recipient_public, home, self, fulfilled_creation)).start()
		
		
		self.dialog.dismiss()

	def show_alert_dialog(self):
		cancel_btn = MDFlatButton(text="CANCEL", on_release=self.close_dialog)
		enter_btn = MDFlatButton(text="ENTER") #on release close the dialog box and send the private key to a variable

		if not self.dialog:
			self.dialog = MDDialog(
                title="Private Key Required:",
                text="",
				content_cls=EscrowNotificationPrompt(),
                buttons=[
                    cancel_btn, enter_btn
                ],
            )
		self.dialog.open()

class PersonalHomeScreen(MDScreen):

	def __init__(self, **kwargs):
		super(PersonalHomeScreen, self).__init__(**kwargs)
		Clock.schedule_once(self.on_start)
        
	def add_card(self, vehicle, fulfilled_tx_car):
		card = CarItemPersonal();
		card.screen = self.name
		card.scrollview = self.ids.content_personal
		card.ids.name_personal.text = vehicle['data']['vehicle']['make']
		card.ids.name_personal.secondary_text = vehicle['data']['vehicle']['model']
		card.ids.name_personal.tertiary_text = vehicle['data']['vehicle']['VIN']
		card.ids.transfer_personal.on_press=lambda *args: card.transfer_dialog(fulfilled_tx_car, self.ids.email.text, self.ids.content_personal, *args)
    	
		self.ids.content_personal.add_widget(card)
        
	def load(self):
    	#Load all vehicles owned by the business
		already_in = []
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
    		
			if temp[-1]['operation'] == 'TRANSFER' and (temp[-1]['asset']['id'] not in already_in):
				check = bdb.transactions.get(asset_id=temp[-1]['asset']['id'])
    			
				if(pub in check[-1]['metadata']['owner']):
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
