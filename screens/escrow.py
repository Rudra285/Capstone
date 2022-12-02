import time
from bigchaindb_driver.common.crypto import PrivateKey
from multiprocessing import Manager
from bigchaindb_driver import BigchainDB

class Escrow():
	manager = Manager()
	PrivateKeyList = manager.list()
	#CardList = manager.dict()
	
	def transfer(self, fulfilled_creation, recipient_tup, recipient_list, all_sender_pvt):
		bdb_root_url = 'https://test.ipdb.io'
		bdb = BigchainDB(bdb_root_url)
		creation_tx = fulfilled_creation
		if(creation_tx['operation'] == 'CREATE'):
			asset_id = creation_tx['id']
		elif(creation_tx['operation'] == 'TRANSFER'):
			asset_id = creation_tx['asset']['id']
		#asset_id = creation_tx['id']
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
			metadata = {'owner': recipient_list}
		)
		
		fulfilled_transfer = bdb.transactions.fulfill(
			prepared_transfer,
			private_keys=all_sender_pvt,
		)
		
		#send the transfer of the car to joe on the bigchaindb network
		sent_transfer = bdb.transactions.send_commit(fulfilled_transfer)
		
		#home.remove_widget(card)
	
	#Only call this for the first time submitting private key
	def verify(self, private_key, public_list, recipient_tup, recipient_list, home, card, fulfilled_creation):
		if len(public_list) == 1:
			try:
				encrypt_private = PrivateKey(private_key)
				decrypted_public = encrypt_private.get_verifying_key().encode().decode()
				print(public_list, decrypted_public)
				if decrypted_public == public_list[0]:
					print("TRUE")
					#ver.value = True
					self.transfer(self, fulfilled_creation, recipient_tup, recipient_list, private_key)
					home.remove_widget(card)
					self.PrivateKeyList[:] = []
				else:
					print('1Incorrect Private Key')
					#return (private_key, True)
				return
				#ver.value = False
			except:
				print('2Incorrect Private Key')
				return
			#return (private_key, False)
		#verify_private = []
		try:
			encrypt_private = PrivateKey(private_key)
			check_pub = encrypt_private.get_verifying_key().encode().decode()
			#If the decoded public key is a owner
			if check_pub in public_list:
				self.PrivateKeyList.append(private_key)
				#self.CardList.append(home)
				#self.CardList[((len(self.CardList)+1))] = home
			else:
				print('M1Incorrect Private Key')
				self.PrivateKeyList[:] = []
				#self.transfer(self, recipient_tup, recipient_list, final_privateKeyList, home, card)
				#return (final_privateKeyList, False)
				#ver.value = False
				return
		except:
			print('M2Incorrect Private Key')
			return
		print("PRIVATE", self.PrivateKeyList)
		print("check", check_pub)
		
		def start_escrow(public_list):
			
			max_limit = 120  # Seconds.
			
			start = time.time()
			condition_met = False
			print(len(self.PrivateKeyList), len(public_list))
			while time.time() - start < max_limit:
				if len(self.PrivateKeyList) == len(public_list):
					print(self.PrivateKeyList)
					condition_met = True
					break
					time.sleep(10)
			print(condition_met)		
			return condition_met
			
		#Only notify other owners the first time verify is called
		
		if len(self.PrivateKeyList) == 1:
			remaining = public_list.copy()
			if check_pub in remaining:
				remaining.remove(check_pub)
			#TODO:notify remaining keys
			#call escrow
			
			result = start_escrow(public_list)
			
			#return result
			if result == True:
				print(check_pub)
				print(public_list)
				print("WROKS")
				
				final_privateKeyList = self.PrivateKeyList.__deepcopy__({})
				self.transfer(self, fulfilled_creation, recipient_tup, recipient_list, final_privateKeyList)
				self.PrivateKeyList[:] = []
			else:
				print("NO")
				#que.put(False)
				self.PrivateKeyList[:] = []
			#ver.value = result
		if len(self.PrivateKeyList) == len(public_list):
			home.remove_widget(card)	
		print(self.PrivateKeyList[:])
		return
