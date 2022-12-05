from kivymd.uix.screen import MDScreen
from kivymd.uix.expansionpanel import MDExpansionPanelThreeLine, MDExpansionPanel
from kivymd.uix.list import ThreeLineListItem
from kivy.properties import StringProperty
from kivy.clock import Clock
from kivymd.uix.boxlayout import MDBoxLayout
from bigchaindb_driver import BigchainDB
from datetime import datetime

class Content(MDBoxLayout):
    header = StringProperty("the name of the business that did maintenance")
    subHeader = StringProperty("phone number for business")
    mileage = StringProperty()

class Maintenance(MDExpansionPanelThreeLine):
    date = StringProperty()
    maintenance = StringProperty()
    owner = StringProperty()

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
		#print(vin)
		#print(query)
		sortingList = []
		for entry in query:
			sortingList.append(entry['metadata']['date'])
		sortingList.sort(key=lambda date: datetime.strptime(date, "%b/%d/%Y %I:%M:%S %p"))
		sortingList.reverse()
		#print(sortingList)
		#TODO: Figure out how to display mileage
		sortedQuery = []
		for localdatetime in sortingList:
			for entry in query:
				if entry['metadata']['date'] == localdatetime:
					sortedQuery.append(entry)
		#print(sortedQuery)
		for sortedEntry in sortedQuery:
			maint = Maintenance()
			maint_info = Content()
			maint.maintenance = sortedEntry['metadata']['maintenance']
			maint.date = sortedEntry['metadata']['date']
			owners = ''
			for i in sortedEntry['metadata']['owner']:
				owners = owners + i + ', '
			owners = owners[:-2]
			maint.owner = 'Owner: ' + owners
			logType = sortedEntry['metadata']['type']
			if logType == 'maint':
				company = sortedEntry['metadata']['company']
				company_query = bdb.assets.get(search = company)
				maint_info.header = 'Mechanic: ' + company
				maint_info.subHeader = 'Phone: ' + company_query[0]['data']['Dealership']['Phone']
				maint_info.mileage = 'Mileage: ' + sortedEntry['metadata']['mileage']
			elif logType == 'transfer':
				maint_info.header = 'New Ownership'
				maint_info.subHeader = 'New Owner: ' + owners
				
			#maint_info.mileage = 'Mileage: ' + sortedEntry['metadata']['mileage']
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
            

