from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty
from bigchaindb_driver import BigchainDB
from bigchaindb_driver.crypto import generate_keypair
import json
import os

class BusinessCreateAccountScreen(MDScreen):
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
		print("Create Account Button Clicked")

		#get the input for the email
		email = self.ids.business_create_email.text
		print(email)

        	#get the input for the password
		password = self.ids.business_create_password.text
		print(password)

        	#Input for the business name
		name = self.ids.business_create_name.text
		print(name)

        	#Input for the business street address
		street = self.ids.business_create_street.text
		print(street)

        	#Input for the business city location
		city = self.ids.business_create_city.text
		print(city)

        	#Input for the business province location
		prov = self.ids.business_create_prov.text
		print(prov)

        	#Input for the business country location
		country = self.ids.business_create_country.text
		print(country)

        	#Input for the business phone number
		phone = self.ids.business_create_phone.text
		print(phone)
		
		postal = self.ids.business_create_postal.text
		print(postal)
		
        	#Generate Keypair
		user_key = generate_keypair()
    	
    		#Get user data from JSON into a dictionary
		json_path = os.path.dirname(os.path.abspath("business.json")) + '/business.json'
		with open(json_path, 'r') as b_users:
			user_data = json.load(b_users)
		b_users.close()
    	
    		#Add new user data to dictionary
		user_data[email] = []
		user_data[email].append(password)
		user_data[email].append(name)
		user_data[email].append(user_key.public_key)
		user_data[email].append(user_key.private_key)
    	
    		#Write updated user data to JSON file
		with open(json_path, 'w') as b_users:
			json.dump(user_data, b_users)
		b_users.close()
    	
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

	def goBack(self, app):
            app.root.current = 'business_login_screen'
