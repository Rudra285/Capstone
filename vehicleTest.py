#!/usr/bin/python3

from bigchaindb_driver import BigchainDB
from bigchaindb_driver.crypto import generate_keypair
from time import sleep
from sys import exit

joe, sana = generate_keypair(), generate_keypair()

bdb_root_url = 'https://test.ipdb.io'  # Use YOUR BigchainDB Root URL here

bdb = BigchainDB(bdb_root_url)

vehicle_asset = {
    'data': {
        'vehicle': {
            'make': 'Lincoln',
            'model': 'MKX',
            'year': '2008',
            'Body': 'SUV',
        },
    },
}

vehicle_asset_metadata = {
    'maintenance': 'new alternator installed'
}

prepared_creation_tx = bdb.transactions.prepare(
    operation='CREATE',
    signers=joe.public_key,
    asset=vehicle_asset,
    metadata=vehicle_asset_metadata
)

fulfilled_creation_tx = bdb.transactions.fulfill(
    prepared_creation_tx,
    private_keys=joe.private_key
)

sent_creation_tx = bdb.transactions.send_commit(fulfilled_creation_tx)

txid = fulfilled_creation_tx['id']

asset_id = txid

transfer_asset = {
    'id': asset_id
}

output_index = 0
output = fulfilled_creation_tx['outputs'][output_index]

transfer_input = {
    'fulfillment': output['condition']['details'],
    'fulfills': {
        'output_index': output_index,
        'transaction_id': fulfilled_creation_tx['id']
    },
    'owners_before': output['public_keys']
}

prepared_transfer_tx = bdb.transactions.prepare(
    operation='TRANSFER',
    asset=transfer_asset,
    inputs=transfer_input,
    recipients=sana.public_key,
)

fulfilled_transfer_tx = bdb.transactions.fulfill(
    prepared_transfer_tx,
    private_keys=joe.private_key,
)

sent_transfer_tx = bdb.transactions.send_commit(fulfilled_transfer_tx)

print("Is sana the owner?",
    sent_transfer_tx['outputs'][0]['public_keys'][0] == sana.public_key)

print("Was joe the previous owner?",
    fulfilled_transfer_tx['inputs'][0]['owners_before'][0] == joe.public_key)
    
print("Metadata?", bdb.metadata.get(search='new alternator installed'))
print("Data?", bdb.assets.get(search='MKX'))

