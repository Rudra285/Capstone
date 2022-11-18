import time
from bigchaindb_driver.common.crypto import PrivateKey
from kivy.clock import mainthread

class Escrow():
	PrivateKeyList = []
	
	def __init__(self):
        	# execute the base constructor
        	Thread.__init__(self)
        	# set a default value
        	self.r = None
        	self.pub = None
	
	#Only call this for the first time submitting private key
	
	def verify(self, private_key, public_list):
		if len(public_list) == 1:
			encrypt_private = PrivateKey(private_key)
			decrypted_public = encrypt_private.get_verifying_key().encode().decode()
			print(public_list, decrypted_public)
			if decrypted_public == public_list[0]:
				print("TRUE")
				return (private_key, True)
			print("FALSE")
			return (private_key, False)
		#verify_private = []
		encrypt_private = PrivateKey(private_key)
		check_pub = encrypt_private.get_verifying_key().encode().decode()
		#If the decoded public key is a owner
		if check_pub in public_list:
			self.PrivateKeyList.append(private_key)
		else:
			print("NOT TRUE")
			final_privateKeyList = self.PrivateKeyList.copy()
			PrivateKeyList.clear()
			return (final_privateKeyList, False)
		print("PRIVATE", self.PrivateKeyList)
		print("check", check_pub)
		@mainthread
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
				self.r = result
				self.pub = check_pub
				print("WROKS")
			else:
				print("NO")
			final_privateKeyList = self.PrivateKeyList.copy()
			self.PrivateKeyList.clear()
			return (final_privateKeyList, result)
		return "Nothing"
