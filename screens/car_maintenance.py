from kivymd.uix.screen import MDScreen
from kivymd.uix.expansionpanel import MDExpansionPanelOneLine, MDExpansionPanel
from kivymd.uix.list import ThreeLineListItem
from kivy.properties import StringProperty
from kivy.clock import Clock
from kivymd.uix.boxlayout import MDBoxLayout
from bigchaindb_driver import BigchainDB

class Content(MDBoxLayout):
    businessName = StringProperty("the name of the business that did maintenance")
    businessNumber = StringProperty("phone number for business")
    date = StringProperty()

class Maintenance(MDExpansionPanelOneLine):
    maintenance = StringProperty()



class CarMaintenanceScreen(MDScreen):
	
	LastScreen = ''

	def __init__(self, **kwargs):
		super(CarMaintenanceScreen, self).__init__(**kwargs)
		Clock.schedule_once(self.on_start)
        
	def load(self, vin, screen):
		self.LastScreen = screen
		bdb_root_url = 'https://test.ipdb.io'
		bdb = BigchainDB(bdb_root_url)
		 
		query = bdb.metadata.get(search = vin)
		for entry in query:
			maint = Maintenance()
			maint_info = Content()
			maint.maintenance = entry['metadata']['maintenance']
			maint_info.date = entry['metadata']['date']
			company = entry['metadata']['company']
			company_query = bdb.assets.get(search = company)
			maint_info.businessName = company
			maint_info.businessNumber = company_query[0]['data']['Dealership']['Phone']
			self.ids.content_maintenance.add_widget(MDExpansionPanel(
    			icon = "car-wrench",
    			content=maint_info,
    			panel_cls=maint))
    		
	def on_start(self, *args):
		pass
	
	def goBack(self, root, app):
		root.manager.get_screen(self.LastScreen).load()
		self.ids.content_maintenance.clear_widgets()
		app.root.current = self.LastScreen
            

