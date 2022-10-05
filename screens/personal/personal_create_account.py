from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty


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

    