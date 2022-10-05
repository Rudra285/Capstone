from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty


class PersonalLoginScreen(MDScreen):

    email_prompt = StringProperty("Email")
    password_prompt = StringProperty("Password")
    btn_text = StringProperty("Login")
    email = StringProperty()
    password = StringProperty()


    def loginButtonClicked(self):
        print("Login Button Clicked")

        #Take the input for the email
        email = self.ids.personal_login_email.text
        print(email)

        #take the input for the password
        password = self.ids.personal_login_password.text
        print(password)

