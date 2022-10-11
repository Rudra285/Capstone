from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty
import os
import json

class BusinessLoginScreen(MDScreen):
    email_prompt = StringProperty("Email")
    password_prompt = StringProperty("Password")
    btn_text = StringProperty("Login")
    email = StringProperty()
    password = StringProperty()


    def loginButtonClicked(self, root, app):
        print("Login Button Clicked")

        #get the input for the email
        email = self.ids.business_login_email.text
        print(email)


        #get the input for the password
        password = self.ids.business_login_password.text
        print(password)
        
        #Check JSON file for existing account
        json_path = os.path.dirname(os.path.abspath("business.json")) + '/business.json'
        with open(json_path, 'r') as b_users:
            user_data = json.load(b_users)
        b_users.close()
        
        #Check email with corresponding password
        checklist = user_data.get(email)
        if checklist == None:
            print('No value')
        else:
            check = checklist[0]
            if check == password:
                print('verified')
                app.root.current = 'business_home_screen'
            else:
                print('Account DNE')

        #TODO Make sure the email and password are not empty

        def goBack(self, app):
            app.root.current = 'startup_screen'
