from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty
import os
import json

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
        
        #Check JSON file for existing account
        json_path = os.path.dirname(os.path.abspath("personal.json")) + '/personal.json'
        with open(json_path, 'r') as p_users:
            user_data = json.load(p_users)
        p_users.close()
        
        #Check email with corresponding password
        checklist = user_data.get(email)
        if checklist == None:
            print('No value')
        else:
            check = checklist[0]
            if check == password:
                print('verified')
                app.root.current = 'personal_home_screen'
            else:
                print('Account DNE')

    def goBack(self, app):
        app.root.current = 'startup_screen'

