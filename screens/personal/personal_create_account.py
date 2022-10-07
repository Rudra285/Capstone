from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty
from bigchaindb_driver.crypto import generate_keypair
import json
import os

class PersonalCreateAccountScreen(MDScreen):
    email_prompt = StringProperty("Account Email")
    name_prompt = StringProperty("Enter your Name")
    password_prompt = StringProperty("Enter your Password")
    btn_text = StringProperty("Create Account")
    email = StringProperty()
    password = StringProperty()
    name = StringProperty()

    def onClick(self):
        print("Create Account Button Clicked")

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
        
        #Get user data from JSON into a dictionary
        json_path = os.path.dirname(os.path.abspath("personal.json")) + '/personal.json'
        with open(json_path, 'r') as p_users:
            user_data = json.load(p_users)
        p_users.close()
        
        #Add new user data to dictionary
        user_data[email] = []
        user_data[email].append(password)
        user_data[email].append(name)
        user_data[email].append(user_key.public_key)
        user_data[email].append(user_key.private_key)
        
        #Write updated user data to JSON file
        with open(json_path, 'w') as p_users:
            json.dump(user_data, p_users)
        p_users.close()
