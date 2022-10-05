from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty


class BusinessLoginScreen(MDScreen):
    email_prompt = StringProperty("Email")
    password_prompt = StringProperty("Password")
    btn_text = StringProperty("Login")
    email = StringProperty()
    password = StringProperty()


    def loginButtonClicked(self):
        print("Login Button Clicked")

        #get the input for the email
        email = self.ids.business_login_email.text
        print(email)


        #get the input for the password
        password = self.ids.business_login_password.text
        print(password)

        #TODO Make sure the email and password are not empty



