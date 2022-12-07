import time
from bigchaindb_driver.common.crypto import PrivateKey
from multiprocessing import Manager
from bigchaindb_driver import BigchainDB
from datetime import datetime

class Escrow():
	manager = Manager()
	PrivateKeyList = manager.list()

	def log(self, public_sign, private_key, owner_names, vin):
		
		#Establish connection to BigchainDB
		bdb_root_url = 'https://test.ipdb.io'
		bdb = BigchainDB(bdb_root_url)
		
		#Get date and time for log creation
		dateTimeObj = datetime.now()
		localtime = dateTimeObj.strftime("%b/%d/%Y %I:%M:%S %p")
		
		#Query BigchainDB for the vechicle VIN
		carQuery = bdb.assets.get(search = vin)
		carQuery = carQuery[0]
		info = bdb.transactions.get(asset_id = carQuery['id'])
		
		car_key = info[0]['inputs'][0]['owners_before'][0] #Get vehicle's public key
		
		#Prepare the creation of log
		maint_data = 'Change Ownership'
		prepared_creation_tx_maintenance = bdb.transactions.prepare(
			operation='CREATE',
			signers=public_sign,
			recipients=car_key,
			metadata= {'maintenance': maint_data, 'date': localtime, 'vin': vin, 'type': 'transfer', 'owner': owner_names}
		)

		#fulfill the creation of the log
		fulfilled_creation_tx_maintenance = bdb.transactions.fulfill(
			prepared_creation_tx_maintenance,
			private_keys=private_key
		)
		
		#send the creation of the log to BigchainDB
		sent_creation_tx_maintenance = bdb.transactions.send_commit(fulfilled_creation_tx_maintenance)
		
	def transfer(self, fulfilled_creation, recipient_tup, recipient_list, all_sender_pvt, recipient_names):
		
		#Establish connection to BigchainDB
		bdb_root_url = 'https://test.ipdb.io'
		bdb = BigchainDB(bdb_root_url)
		
		#Prepare proper transaction input for transfer preparation
		creation_tx = fulfilled_creation

		if(creation_tx['operation'] == 'CREATE'):
			asset_id = creation_tx['id']
		elif(creation_tx['operation'] == 'TRANSFER'):
			asset_id = creation_tx['asset']['id']
			
		transfer_asset = {
			'id': asset_id,
		}
		
		output_index = 0
		output = creation_tx['outputs'][output_index]
		transfer_input = {
			'fulfillment': output['condition']['details'],
			'fulfills': {
				'output_index': output_index,
				'transaction_id': creation_tx['id']
			},
			'owners_before': output['public_keys']
		}

		#prepare the transfer of car
		prepared_transfer = bdb.transactions.prepare(
			operation='TRANSFER',
			asset=transfer_asset,
			inputs=transfer_input,
			recipients=recipient_tup,
			metadata = {'owner_key': recipient_list, 'owner_name': recipient_names}
		)
		
		#Fulfill the transfer of car
		fulfilled_transfer = bdb.transactions.fulfill(
			prepared_transfer,
			private_keys=all_sender_pvt,
		)

		#send the transfer of the car to joe on the bigchaindb network
		sent_transfer = bdb.transactions.send_commit(fulfilled_transfer)
	
	def verify(self, private_key, public_list, recipient_tup, recipient_list, card, fulfilled_creation, recipient_names, vin):
		
		#If transfering from one owner
		if len(public_list) == 1:
			#Error check for invalid private key input
			try:
				encrypt_private = PrivateKey(private_key)
				decrypted_public = encrypt_private.get_verifying_key().encode().decode()
				
				#If private key is valid
				if decrypted_public == public_list[0]:
					#Transfer Vehicle
					self.transfer(self, fulfilled_creation, recipient_tup, recipient_list, private_key, recipient_names)
					
					#Add transfer to vehicle history
					self.log(self, public_list[0], private_key, recipient_names, vin)
					
					card.remove_card()
					self.PrivateKeyList[:] = []
				else:
					print('Incorrect Private Key')
			except:
				print('Incorrect Private Key input')
			return
		
		#Only if vehicle is currently owned by multiple accounts	
		try:
			encrypt_private = PrivateKey(private_key)
			check_pub = encrypt_private.get_verifying_key().encode().decode()
			
			#If the decoded public key is a owner
			if check_pub in public_list:
				self.PrivateKeyList.append(private_key) #Add to private key list
			else:
				print('Incorrect Private Key')
				self.PrivateKeyList[:] = [] #Clear private keys
				return
		except:
			print('Incorrect Private Key input')
			return
		
		def start_escrow(public_list):
			max_limit = 120  #Seconds.
			
			start = time.time()
			condition_met = False
			
			while time.time() - start < max_limit:
				if len(self.PrivateKeyList) == len(public_list):
					condition_met = True
					break
					time.sleep(10)				
			return condition_met
		
		#Only call escrow the first time a private key is inputted
		if len(self.PrivateKeyList) == 1:
			#Call escrow
			result = start_escrow(public_list)
			
			#If escrow is successful
			if result == True:
				print("Escrow Successful")
				
				final_privateKeyList = self.PrivateKeyList.__deepcopy__({})
				
				#Get the private key for log transaction
				if public_list[0] == check_pub:
					history_pvt = private_key
				
				#Transfer vehicle
				self.transfer(self, fulfilled_creation, recipient_tup, recipient_list, final_privateKeyList ,recipient_names)
				
				#Add transfer to vehicle History
				self.log(self, public_list[0], history_pvt, recipient_names, vin)
				self.PrivateKeyList[:] = [] #Clear private keys
			else:
				print("Timeout")
				self.PrivateKeyList[:] = []
		return
