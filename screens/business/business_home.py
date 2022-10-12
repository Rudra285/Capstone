from kivymd.uix.screen import MDScreen
from kivy.uix.scrollview import ScrollView
from kivymd.uix.label import MDLabel
from kivy.properties import StringProperty
from kivymd.uix.card import MDCard
from kivymd.uix.behaviors import RectangularElevationBehavior
from kivy.clock import Clock

class CardItem(MDCard, RectangularElevationBehavior):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.elevation = 3


class BusinessHomeScreen(MDScreen):

    submit = StringProperty("Submit button pressed")

    def __init__(self, **kwargs):
        super(BusinessHomeScreen, self).__init__(**kwargs)
        Clock.schedule_once(self.on_start)
    
    def on_start(self, *args):
        #TODO IF any cars are owned determine how many, put that in a variable
        ##Example of 10 CardItem()'s being created
        for x in range(10):
            self.ids.content.add_widget(CardItem())

        ##TODO figure out how to change the title and subtitle in each cardItem
        ##TODO based on the vehicles being shown. 
        ##TODO example: title = Make, subtitle = Model

    # def clock_next(self, app):
    #     Clock.schedule_once(self.next)

    def next(self):
        self.ids.form.load_next(mode="next")
        self.ids.customer_label.text_color=(76/255, 175/255, 80/255, 1)
        self.ids.progress_zero.value = 100
        self.ids.customer_icon.text_color = (76/255, 175/255, 80/255, 1)
        self.ids.customer_icon.icon = "check-decagram"

    def next_one(self):
        self.ids.form.load_next(mode="next")
        self.ids.maint_label.text_color=(76/255, 175/255, 80/255, 1)
        self.ids.progress_one.value = 100
        self.ids.maint_icon.text_color = (76/255, 175/255, 80/255, 1)
        self.ids.maint_icon.icon = "check-decagram"

    def previous(self):
        self.ids.form.load_previous()
        self.ids.customer_label.text_color=(1, 1, 1, 1)
        self.ids.progress_zero.value = 0
        self.ids.customer_icon.icon = "numeric-1-circle"
        self.ids.customer_icon.text_color = (1, 1, 1, 1)


    def previous_one(self):
        self.ids.form.load_previous()
        self.ids.maint_label.text_color = (1, 1, 1, 1)
        self.ids.progress_one.value = 0
        self.ids.maint_icon.icon = "numeric-2-circle"
        self.ids.maint_icon.text_color = (1, 1, 1, 1)







