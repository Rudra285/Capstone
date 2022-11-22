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

class PersonalPrivateKey(MDBoxLayout):
	pass
	
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

        #get the input for the email
		email = self.ids.personal_create_email.text
		print(email)

        #get the input for the password
		password = self.ids.personal_create_password.text
		print(password)

		name = self.ids.personal_create_name.text
		print(name)
        
        #Generate Keypair
		user_key = generate_keypair()
        
        #POST user data to "users" database
		URL = "https://1r6m03cirj.execute-api.us-west-2.amazonaws.com/test/users"
        
		user = requests.get(url = URL, params = {'email': email})
		data = user.json()
        
		if len(data['Items']) == 0:
        	#Send POST
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
        		'account': 'P'
        	}
        	
			post = requests.post(url = URL, json = new_user)
        	
        	#Show Private Key
			if not self.dialog:
				prompt = PersonalPrivateKey()
				prompt.ids.key.text = user_key.private_key
				self.dialog = MDDialog(
        			title = "Private Key (DON'T FORGET)",
        			type = "custom",
        			content_cls = prompt,
        			buttons = [
        				MDIconButton(
        					icon = "content-copy",
        					on_press = self.copy_clip
        				),
        				MDFlatButton(
        					text = "OK",
        					on_press = self.close_key
        				)
        			]
        		)
				self.dialog.open()
		else:
			print('Account already exists!')
        	
	def close_key(self, obj):
		self.dialog.dismiss()
    
	def copy_clip(self, obj):
		pyclip.copy(self.dialog.content_cls.ids.key.text)

	def goBack(self, app):
		app.root.current = 'personal_login_screen'
