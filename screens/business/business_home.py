from kivymd.uix.screen import MDScreen
from kivy.uix.scrollview import ScrollView
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.behaviors import RectangularElevationBehavior
from kivy.clock import Clock

class CardItem(MDCard, RectangularElevationBehavior):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.elevation = 3


class BusinessHomeScreen(MDScreen):

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



