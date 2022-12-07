from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty
from bigchaindb_driver.crypto import generate_keypair
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.button import MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout
import pyclip
import hashlib
import os
import requests
	
class PersonalCreateAccountScreen(MDScreen):
	email_prompt = StringProperty("Account Email")
	name_prompt = StringProperty("Enter your Name")
	password_prompt = StringProperty("Enter your Password")
	btn_text = StringProperty("Create Account")
	email = StringProperty()
	password = StringProperty()
	name = StringProperty()
	dialog = None

	def onClick(self):
		email = self.ids.personal_create_email.text #Input for the email
		password = self.ids.personal_create_password.text #Input for the password
		name = self.ids.personal_create_name.text #Input for the name

		user_key = generate_keypair() #Generate Keypair
        
        	#POST user data to "users" database
		URL = "https://1r6m03cirj.execute-api.us-west-2.amazonaws.com/test/users"
		
		#Error check for any empty fields
		if email != '' and password != '' and name != '':
			user = requests.get(url = URL, params = {'email': email})
			data = user.json()
			
			#If no account exists for email
			if len(data['Items']) == 0:
				self.ids.create_status.text =''
				
				#Send POST
				salt = os.urandom(32) #A new salt for this user
				encoded_passwd = password.encode('utf-8') + salt #Encode password and add salt
				hashed_passwd = hashlib.pbkdf2_hmac('sha256', encoded_passwd, salt, 100000) #Hash password
				
				#Create entry
				new_user = {
					'email': email,
					'name': name,
					'salt': salt.hex(),
					'password': hashed_passwd.hex(),
					'publicKey': user_key.public_key,
					'account': 'P'
				}
				
				post = requests.post(url = URL, json = new_user)
				
				#Show Private Key
				if not self.dialog:
					self.dialog = MDDialog(
					title = "Private Key (DON'T FORGET)",
					text = user_key.private_key,
					buttons = [
						MDIconButton(
							icon = "content-copy",
							on_press = self.copy_clip
						)
					]
					)
					self.dialog.open()
			else:
				self.ids.create_status.text = 'Account already exists!'
			
			self.ids.personal_create_email.text = ''
			self.ids.personal_create_password.text = ''
			self.ids.personal_create_name.text = ''
		else:
			self.ids.create_status.text = 'Fill in all the fields'
    
	def copy_clip(self, obj):
	
		#Copy Private Key to clipboard
		pyclip.copy(self.dialog.text)
		self.dialog.dismiss()
		self.dialog = None

	def goBack(self, app):
		self.ids.create_status.text = ''
		self.ids.personal_create_email.text = ''
		self.ids.personal_create_password.text = ''
		self.ids.personal_create_name.text = ''
		app.root.current = 'personal_login_screen'
