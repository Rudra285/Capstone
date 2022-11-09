from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty
import os
import requests
import hashlib

class BusinessLoginScreen(MDScreen):
    email_prompt = StringProperty("Email")
    password_prompt = StringProperty("Password")
    btn_text = StringProperty("Login")
    email = StringProperty()
    password = StringProperty()


    def loginButtonClicked(self, root, app):

        #get the input for the email
        email = self.ids.business_login_email.text
        print(email)


        #get the input for the password
        password = self.ids.business_login_password.text
        print(password)
        
        #check GET request for existing account
        URL = "https://1r6m03cirj.execute-api.us-west-2.amazonaws.com/test/users"
        
        user = requests.get(url = URL, params = {'email': email})
        data = user.json()
        
        if len(data['Items']) == 0:
        	print('Account does not exist!')
        else:
        	if data['Items'][0]['account']['S'] == 'B':
        		salt = bytes.fromhex(data['Items'][0]['salt']['B'])
        		encoded_input = password.encode('utf-8') + salt
        		hashed_input = hashlib.pbkdf2_hmac('sha256', encoded_input, salt, 100000)
        		check = hashed_input.hex()
        		
        		if data['Items'][0]['password']['B'] == check:
        			root.manager.get_screen('business_home_screen').ids.email.text = email
        			root.manager.get_screen('business_home_screen').load()
        			app.root.current = 'business_home_screen'
        			print('Login Success')
        		else:
        			print('Password does not match!')

        #TODO Make sure the email and password are not empty

        def goBack(self, app, root):
            app.root.current = 'startup_screen'
