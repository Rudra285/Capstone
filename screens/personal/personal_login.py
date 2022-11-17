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
        if not self.dialog:
            self.dialog = MDDialog(
                title="Acknowledgment Required For Security Reasons:",
                text="Do not create an account on anyone elses device but your own.\nUpon account creation a private key will be displayed to you.\nYou are responsible, as the account owner, to protect this private key.\nWithout access to this private key no transfers can be made.\nIt is recommended that the private key is stored in an encrypted device or paper that is kept in a secure location.",
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                    ),
                    MDFlatButton(
                        text="ACCEPT",
                    ),
                ],
            )
        self.dialog.open()


    def loginButtonClicked(self, root, app):

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

