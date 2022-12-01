from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty
from bigchaindb_driver import BigchainDB
from bigchaindb_driver.crypto import generate_keypair
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.button import MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout
import pyclip
import requests
import hashlib
import os
			
class BusinessCreateAccountScreen(MDScreen):
	dialog = None
	email_prompt = StringProperty("Account Email")
	business_name = StringProperty("Business Name")
	password_prompt = StringProperty("Password")
	phone_prompt = StringProperty("Business Phone Number")
	street_prompt = StringProperty("Street Address of your Business")
	city_prompt = StringProperty("City")
	prov_prompt = StringProperty("Province")
	country_prompt = StringProperty("Country")
	postal_prompt = StringProperty("Postal Code")

	btn_text = StringProperty("Create Account")

	email = StringProperty()
	password = StringProperty()
	name = StringProperty()
	phone = StringProperty()
	street = StringProperty()
	city = StringProperty()
	prov = StringProperty()
	country = StringProperty()
	postal = StringProperty()

	def onClick(self):
        #Establish connection to BigChainDB
		bdb_root_url = 'https://test.ipdb.io'  # Use YOUR BigchainDB Root URL here
		bdb = BigchainDB(bdb_root_url)

		#get the input for the email
		email = self.ids.business_create_email.text

        	#get the input for the password
		password = self.ids.business_create_password.text
		print(password)

        	#Input for the business name
		name = self.ids.business_create_name.text

        	#Input for the business street address
		street = self.ids.business_create_street.text

        	#Input for the business city location
		city = self.ids.business_create_city.text

        	#Input for the business province location
		prov = self.ids.business_create_prov.text

        	#Input for the business country location
		country = self.ids.business_create_country.text

        	#Input for the business phone number
		phone = self.ids.business_create_phone.text
		
		postal = self.ids.business_create_postal.text
		
        	#Generate Keypair
		user_key = generate_keypair()
		
		#POST user data to "users" database
		URL = "https://1r6m03cirj.execute-api.us-west-2.amazonaws.com/test/users"
		
		if email != '' and password != '' and name != '' and street != '' and city != '' and prov != '' and country != '' and phone != '' and postal != '':
			user = requests.get(url = URL, params = {'email': email})
			data = user.json()
			
			if len(data['Items']) == 0:
				#Send POST request
				salt = os.urandom(32) # A new salt for this user
				#Encode password and add salt
				encoded_passwd = password.encode('utf-8') + salt
				#Hash password
				hashed_passwd = hashlib.pbkdf2_hmac('sha256', encoded_passwd, salt, 100000)
				
				#Create entry
				new_user = {
					'email': email,
					'name': name,
					'salt': salt.hex(),
					'password': hashed_passwd.hex(),
					'publicKey': user_key.public_key,
					'account': 'B'
				}
				
				post = requests.post(url = URL, json = new_user)
				#Create business dealership
				dealership = {
					'data': {
						'Dealership': {
							'Name': name,
							'Street': street,
							'Country': country,
							'Province': prov,
							'City': city,
							'Postal Code': postal,
							'Phone': phone
						}
					}
				}
				
				#Prepare the creation of the dealership
				prepared_creation_tx_dealership = bdb.transactions.prepare(
					operation='CREATE',
					signers=user_key.public_key,
					asset=dealership,
					metadata = {'type': 'dealer'}
				)
				
				#Fulfill the creation of the dealership by signing with dealer private key
				fulfilled_creation_tx_dealership = bdb.transactions.fulfill(
					prepared_creation_tx_dealership,
					private_keys=user_key.private_key
				)
				
				#send the creation of the dealership to bigchaindb
				sent_creation_tx_dealership = bdb.transactions.send_commit(fulfilled_creation_tx_dealership)
				
				#get the txid of the dealership creation
				txid_dealership = fulfilled_creation_tx_dealership['id']
				print("What is the transaction ID for the creation of the dealership?", txid_dealership)
				print("Dealership:", dealership)
				
				#Show Private Key
				if not self.dialog:
					self.dialog = MDDialog(
						title = "Private Key (DON'T FORGET)",
						text = user_key.private_key,
						buttons = [
							MDIconButton(
								icon = "content-copy",
								on_release = self.copy_clip
							)
						]
					)
					self.dialog.open()
			else:
				print('Account already exists!')
			
			#TODO: display error on screen not in terminal
			self.ids.business_create_email.text = ''
			self.ids.business_create_password.text = ''
			self.ids.business_create_name.text = ''
			self.ids.business_create_street.text = ''
			self.ids.business_create_city.text = ''
			self.ids.business_create_prov.text = ''
			self.ids.business_create_country.text = ''
			self.ids.business_create_phone.text = ''
			self.ids.business_create_postal.text = ''
		else:
			print('Fill in all the fields')
		
	def copy_clip(self, obj):
		pyclip.copy(self.dialog.text)
		self.dialog.dismiss()
		self.dialog = None
		

	def goBack(self, app):
		app.root.current = 'business_login_screen'
