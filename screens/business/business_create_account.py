from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty
from bigchaindb_driver import BigchainDB
from bigchaindb_driver.crypto import generate_keypair
import json
import os

class BusinessCreateAccountScreen(MDScreen):
    email_prompt = StringProperty("Enter your Account Email")
    business_name = StringProperty("Enter your Business Name")
    password_prompt = StringProperty("Enter your Password")
    btn_text = StringProperty("Create Account")
    email = StringProperty()
    password = StringProperty()
    name = StringProperty()

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

        name = self.ids.business_create_name.text
        print(name)
        
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
    				'Country': 'Canada',
    				'Province': 'Alberta',
    				'City': 'Edmonton',
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
