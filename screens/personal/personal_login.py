from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
import os
import requests
import hashlib

class PersonalLoginScreen(MDScreen):

    email_prompt = StringProperty("Email")
    password_prompt = StringProperty("Password")
    btn_text = StringProperty("Login")
    email = StringProperty()
    password = StringProperty()
    dialog = None

    def create_personal_account_clicked(self, root, app):
    	
    	#Show disclaimer for private key
        cancel_btn = MDFlatButton(text="CANCEL", on_release=self.close_dialog)
        accept_btn = MDFlatButton(text="ACCEPT", on_release=lambda *args: self.create_account_screen(app, *args))

        if not self.dialog:
            self.dialog = MDDialog(
                title="Acknowledgment Required For Security Reasons:",
                text="Do not create an account on anyone elses device but your own.\nUpon account creation a private key will be displayed to you.\nYou are responsible, as the account owner, to protect this private key.\nWithout access to this private key no transfers can be made.\nIt is recommended that the private key is stored in an encrypted device or paper that is kept in a secure location.",
                buttons=[
                    cancel_btn, accept_btn
                ],
            )
        self.dialog.open()

    def close_dialog(self, obj):
        self.dialog.dismiss()

    def create_account_screen(self, app, *args):
        self.dialog.dismiss()
        app.root.current = 'personal_create_account_screen'

    def loginButtonClicked(self, root, app):
    	email = self.ids.personal_login_email.text #Input for the email
    	password = self.ids.personal_login_password.text #Input for the password
    	
    	#check GET request for existing account
    	URL = "https://1r6m03cirj.execute-api.us-west-2.amazonaws.com/test/users"
    	
    	#Error check for empty fields
    	if email != '' and password != '':
    		user = requests.get(url = URL, params = {'email': email})
    		data = user.json()
    		
    		#If account doesn't exist
    		if len(data['Items']) == 0:
    			self.ids.login_status.text = 'Account does not exist!'
    			self.ids.personal_login_email.text = ''
    			self.ids.personal_login_password.text = ''
    		else:
    			#If account found is personal account
    			if data['Items'][0]['account']['S'] == 'P':
    				
    				#Verify password
    				salt = bytes.fromhex(data['Items'][0]['salt']['B'])
    				encoded_input = password.encode('utf-8') + salt
    				hashed_input = hashlib.pbkdf2_hmac('sha256', encoded_input, salt, 100000)
    				check = hashed_input.hex()
    				
    				if data['Items'][0]['password']['B'] == check:
    					root.manager.get_screen('personal_home_screen').ids.email.text = email
    					self.ids.login_status.text = ''
    					self.ids.personal_login_email.text = ''
    					self.ids.personal_login_password.text = ''
    					root.manager.get_screen('personal_home_screen').load()
    					app.root.current = 'personal_home_screen'
    				else:
    					self.ids.login_status.text = 'Password does not match!'
    					self.ids.personal_login_password.text = ''
    			else:
    				self.ids.login_status.text = 'Account does not exist!'
    				self.ids.personal_login_email.text = ''
    				self.ids.personal_login_password.text = ''
    	else:
    		self.ids.login_status.text = 'Fill in all the fields'

    def goBack(self, app):
    	self.ids.login_status.text = ''
    	self.ids.personal_login_email.text = ''
    	self.ids.personal_login_password.text = ''
    	app.root.current = 'startup_screen'
