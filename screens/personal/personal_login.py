from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty
import os
import requests
import hashlib

class PersonalLoginScreen(MDScreen):

    email_prompt = StringProperty("Email")
    password_prompt = StringProperty("Password")
    btn_text = StringProperty("Login")
    email = StringProperty()
    password = StringProperty()


    def loginButtonClicked(self, root, app):
        print("Login Button Clicked")

        #Take the input for the email
        email = self.ids.personal_login_email.text
        print(email)

        #take the input for the password
        password = self.ids.personal_login_password.text
        print(password)
        
        #check GET request for existing account
        URL = "https://1r6m03cirj.execute-api.us-west-2.amazonaws.com/test/users"
        
        user = requests.get(url = URL, params = {'email': email})
        data = user.json()
        
        if len(data['Items']) == 0:
        	print('Account does not exist!')
        else:
        	if data['Items'][0]['account']['S'] == 'P':
        		 salt = bytes.fromhex(data['Items'][0]['salt']['B'])
        		 encoded_input = password.encode('utf-8') + salt
        		 hashed_input = hashlib.pbkdf2_hmac('sha256', encoded_input, salt, 100000)
        		 check = hashed_input.hex()
        		 
        		 if data['Items'][0]['password']['B'] == check:
        		 	root.manager.get_screen('personal_home_screen').ids.email.text = email
        		 	root.manager.get_screen('personal_home_screen').load()
        		 	app.root.current = 'personal_home_screen'
        		 	print('Login Success')
        		 else:
        		 	print('Password does not match!')

    def goBack(self, app):
        app.root.current = 'startup_screen'

