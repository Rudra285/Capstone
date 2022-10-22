from kivymd.uix.screen import MDScreen
from kivy.clock import Clock
import os
import json
from kivymd.uix.dialog import MDDialog
from kivy.properties import StringProperty
from  kivymd.uix.card import MDCardSwipe
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import IRightBodyTouch
from kivymd.uix.button import MDFlatButton
from bigchaindb_driver import BigchainDB

class TransferPersonalPrompt(MDBoxLayout):
	pass

class CarItemPersonal(MDCardSwipe):
    make = StringProperty()
    model = StringProperty()
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
    	app.root.get_screen('car_maintenance').load(car_VIN)
    	app.root.current = 'car_maintenance'
    
    def transfer_personal(self, fulfilled_creation, current_email, home, *args):
    	bdb_root_url = 'https://test.ipdb.io'
    	bdb = BigchainDB(bdb_root_url)
    	#FOR NOW only transfer back to business
    	business_path = os.path.dirname(os.path.abspath("business.json")) + '/business.json'
    	with open(business_path, 'r') as b_users:
    		business_users = json.load(b_users)
    	b_users.close()
    	email = self.dialog.content_cls.ids.recipient.text
    	dest = business_users.get(email)
    	recipient_pub = dest[-2]
    	personal_path = os.path.dirname(os.path.abspath("personal.json")) + '/personal.json'
    	with open(personal_path, 'r') as p_users:
    		personal_users = json.load(p_users)
    	p_users.close()
    	info = personal_users.get(current_email)
    	sender_pvt = info[-1]
    	
    	creation_tx = fulfilled_creation
    	asset_id = creation_tx['id']
    	transfer_asset = {
    		'id': creation_tx['asset']['id'],
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

class PersonalHomeScreen(MDScreen):

    def __init__(self, **kwargs):
        super(PersonalHomeScreen, self).__init__(**kwargs)
        Clock.schedule_once(self.on_start)
        
    def add_card(self, vehicle, fulfilled_tx_car):
    	card = CarItemPersonal();
    	card.ids.name_personal.text = vehicle['data']['vehicle']['make']
    	card.ids.name_personal.secondary_text = vehicle['data']['vehicle']['model']
    	card.ids.name_personal.tertiary_text = vehicle['data']['vehicle']['VIN']
    	card.ids.transfer_personal.on_press=lambda *args: card.transfer_dialog(fulfilled_tx_car, self.ids.name.text, self.ids.content_personal, *args)
    	
    	self.ids.content_personal.add_widget(card)
        
    def load(self):
    	#Load all vehicles owned by the business
    	#NOTE: THERE is an issue with loading 'TRANSFER'
    	already_in = []
    	bdb_root_url = 'https://test.ipdb.io'
    	bdb = BigchainDB(bdb_root_url)
    	json_path = os.path.dirname(os.path.abspath("personal.json")) + '/personal.json'
    	with open(json_path, 'r') as p_users:
    		user_data = json.load(p_users)
    	p_users.close()
    	email = self.ids.name.text
    	pub = user_data.get(email)[-2]
    	data_list = bdb.metadata.get(search = pub)
    	#print(data_list)
    	for i in data_list:
    		temp = bdb.transactions.get(asset_id=i['id'])
    		#print("FIRST:", temp)
    		#print("ALREADY_IN:",already_in)
    		if temp[-1]['operation'] == 'TRANSFER' and (temp[-1]['asset']['id'] not in already_in):
    			check = bdb.transactions.get(asset_id=temp[-1]['asset']['id'])
    			#print("SECOND:", check)
    			if(check[-1]['metadata']['owner'] == pub):
    				already_in.append(check[-1]['asset']['id'])
    				vehicle = check[0]['asset']
    				self.add_card(vehicle, temp[-1])	

    def on_start(self, *args):
        pass

    def logout(self, root, app):
        app.root.current = 'startup_screen'

    def clock_next(self, app):
        Clock.schedule_once(self.next)
