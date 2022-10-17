from kivymd.uix.screen import MDScreen
from kivy.clock import Clock
import os
import json
from kivymd.uix.dialog import MDDialog
from kivy.properties import StringProperty
from  kivymd.uix.card import MDCardSwipe
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import IRightBodyTouch
from kivymd.uix.button import MDFlatButton

class TransferPrompt(MDBoxLayout):
	pass

class CarItemPersonal(MDCardSwipe):

	##TODO connect the make/model variables to the make/model of the car being created
    make = StringProperty()
    model = StringProperty()
    dialog = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.elevation = 3
	
    def transfer_dialog(self, fulfilled_creation_tx_car, current_email, home, *args):
        if not self.dialog:
            self.dialog = MDDialog(
                title="Transfer Vehicle:",
                type="custom",
                content_cls=TransferPrompt(),
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        on_press = self.close_carlog
                    ),
                    MDFlatButton(
                        text="SUBMIT",
                        on_press = lambda *args: self.transfer_personal(fulfilled_creation_tx_car, current_email, home, *args)
                    ),
                ],
            )
        self.dialog.open()
		
    def close_carlog(self, obj):
		#print(self.ids.name.text)
        self.dialog.dismiss()

    def maintenance_screen(self, app):
        app.root.current = 'car_maintenance'


class PersonalHomeScreen(MDScreen):

    def __init__(self, **kwargs):
        super(PersonalHomeScreen, self).__init__(**kwargs)
        Clock.schedule_once(self.on_start)

    def on_start(self, *args):
        for x in range(10):
            self.ids.content_personal.add_widget(CarItemPersonal())

    def logout(self, root, app):
        app.root.current = 'startup_screen'

    def clock_next(self, app):
        Clock.schedule_once(self.next)