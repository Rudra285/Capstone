from kivymd.uix.screen import MDScreen
from kivymd.uix.expansionpanel import MDExpansionPanelOneLine, MDExpansionPanel
from kivymd.uix.list import ThreeLineListItem
from kivy.properties import StringProperty
from kivy.clock import Clock
from kivymd.uix.boxlayout import MDBoxLayout

class Content(MDBoxLayout):
    businessName = StringProperty("the name of the business that did maintenance")
    businessNumber = StringProperty("phone number for business")
    date = StringProperty("date maintenance was performed")

class Maintenance(MDExpansionPanelOneLine):
    maintenance = StringProperty("this is the maintenance performed")



class CarMaintenanceScreen(MDScreen):

    def __init__(self, **kwargs):
        super(CarMaintenanceScreen, self).__init__(**kwargs)
        Clock.schedule_once(self.on_start)

    def on_start(self, *args):

        for x in range(10):
            self.ids.content_maintenance.add_widget(MDExpansionPanel(
                    icon = "car-wrench",
                    content=Content(),
                    panel_cls=Maintenance()))

