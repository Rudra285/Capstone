from kivymd.uix.screen import MDScreen
from kivymd.uix.expansionpanel import MDExpansionPanelThreeLine, MDExpansionPanel
from kivymd.uix.list import ThreeLineListItem
from kivy.properties import StringProperty
from kivy.clock import Clock
from kivymd.uix.boxlayout import MDBoxLayout
from bigchaindb_driver import BigchainDB
from datetime import datetime
from reportlab.pdfgen import canvas

class Content(MDBoxLayout):
    header = StringProperty()
    subHeader = StringProperty()
    mileage = StringProperty()

class Maintenance(MDExpansionPanelThreeLine):
    date = StringProperty()
    maintenance = StringProperty()
    owner = StringProperty()

class CarMaintenanceScreen(MDScreen):
	
	LastScreen = ''
	vin = ''
	
	def __init__(self, **kwargs):
		super(CarMaintenanceScreen, self).__init__(**kwargs)
		Clock.schedule_once(self.on_start)
        
	def load(self, vin, screen):
		
		#Initialize class variables
		self.LastScreen = screen
		self.vin = vin
		
		#Establish connection to BigchainDB
		bdb_root_url = 'https://test.ipdb.io'
		bdb = BigchainDB(bdb_root_url)
		
		query = bdb.metadata.get(search = vin) #Query for vehicle VIN in metadata
		
		#Sort timestamps in assending order
		sortingList = []
		for entry in query:
			sortingList.append(entry['metadata']['date'])
		sortingList.sort(key=lambda date: datetime.strptime(date, "%b/%d/%Y %I:%M:%S %p"))
		
		#Sort query by timestamp in assending order
		sortedQuery = []
		for localdatetime in sortingList:
			for entry in query:
				if entry['metadata']['date'] == localdatetime:
					sortedQuery.append(entry)
		
		#Add recent mileage data to queried data
		for item in sortedQuery:
			try:
				key = item['metadata']['mileage']
			except:
				item['metadata']['mileage'] = key
		
		sortedQuery.reverse() #Reverse the query list
		
		#Add log item to scrollview
		for sortedEntry in sortedQuery:
			maint = Maintenance()
			maint_info = Content()
			
			#Get Expansion Panel data
			maint.maintenance = sortedEntry['metadata']['maintenance']
			maint.date = sortedEntry['metadata']['date']
			owners = ''
			for i in sortedEntry['metadata']['owner']:
				owners = owners + i + ', '
			owners = owners[:-2]
			maint.owner = 'Owner: ' + owners
			
			#Based on log type, add details accordingly to expanded panel
			logType = sortedEntry['metadata']['type']
			
			if logType == 'maint':
				company = sortedEntry['metadata']['company']
				company_query = bdb.assets.get(search = company) #Query for company name
				maint_info.header = 'Mechanic: ' + company
				maint_info.subHeader = 'Phone: ' + company_query[0]['data']['Dealership']['Phone']
			elif logType == 'transfer':
				maint_info.header = 'New Ownership'
				maint_info.subHeader = 'New Owner: ' + owners
			maint_info.mileage = 'Mileage: ' + sortedEntry['metadata']['mileage']
			
			#Add Log asset to scrollview list
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
	
	def export_pdf(self):
		vin = self.vin
		filename = 'vehicle_history_' + vin + '.pdf'
		
		#Establish connection to BigchainDB
		bdb_root_url = 'https://test.ipdb.io'
		bdb = BigchainDB(bdb_root_url)
		
		#Query BigchainDB for vehicle VIN
		query = bdb.metadata.get(search = vin)
		asset_query = bdb.assets.get(search = vin)
		
		#Sort timestamps in assending order
		sortingList = []
		for entry in query:
			sortingList.append(entry['metadata']['date'])
		sortingList.sort(key=lambda date: datetime.strptime(date, "%b/%d/%Y %I:%M:%S %p"))
		
		#Sort query by timestamp in assending order
		sortedQuery = []
		for localdatetime in sortingList:
			for entry in query:
				if entry['metadata']['date'] == localdatetime:
					sortedQuery.append(entry)
		
		#Add recent mileage data to queried data
		for item in sortedQuery:
			try:
				key = item['metadata']['mileage']
			except:
				item['metadata']['mileage'] = key
		
		sortedQuery.reverse() #Reverse the query list
		
		my_canvas = canvas.Canvas(filename) #Create file
		my_canvas.setLineWidth(.3) #Initialize spacing
		my_canvas.setFont('Helvetica', 24) #Set font size
		
		#Add all vehicle history to pdf
		my_canvas.drawString(30, 750, 'My Garage Vehicle History')
		my_canvas.setFont('Helvetica', 12)
		data = 'Vehicle Identification Number: ' + vin
		my_canvas.drawString(30, 735, data)
		data = 'Make: ' + asset_query[0]['data']['vehicle']['make']
		my_canvas.drawString(30, 720, data)
		data = 'Model: ' + asset_query[0]['data']['vehicle']['model']
		my_canvas.drawString(30, 705, data)
		data = 'Year: ' + asset_query[0]['data']['vehicle']['year']
		my_canvas.drawString(30, 690, data)
		my_canvas.drawString(30, 675, '')
		my_canvas.drawString(30, 660, '')
		space = 660
		
		for entry in sortedQuery:
			owners = ''
			for i in entry['metadata']['owner']:
				owners = owners + i + ', '
			owners = owners[:-2]

			data = entry['metadata']['maintenance']
			my_canvas.drawString(30, space, data)
			space -= 15
			data = 'Date: ' + entry['metadata']['date']
			my_canvas.drawString(30, space, data)
			space -= 15
			data = 'Owner(s): ' + owners
			my_canvas.drawString(30, space, data)
			space -= 15
			logType = entry['metadata']['type']
			
			if logType == 'maint':
				company = entry['metadata']['company']
				company_query = bdb.assets.get(search = company)
				data = 'Mechanic: ' + company
				my_canvas.drawString(30, space, data)
				space -= 15
				data = 'Phone: ' + company_query[0]['data']['Dealership']['Phone']
				my_canvas.drawString(30, space, data)
				space -= 15
				
			data = 'Vehicle Traveled: ' + entry['metadata']['mileage']
			my_canvas.drawString(30, space, data)
			space -= 15
			my_canvas.drawString(30, space, '')
			space -= 15
		
		my_canvas.save() #Save file
            

