from hashlib import sha256
import json
import time
import sys
from flask import Flask, request
import requests
import inspect

class Block:
	def __init__(self, index, transactions, timestamp, previous_hash, nonce=0):
		fi=inspect.getframeinfo((inspect.stack()[0])[0]); print(">>> ", fi.filename, '; ', fi.function, '(); line:', fi.lineno, file=sys.stderr)
		self.index = index
		self.transactions = transactions
		self.timestamp = timestamp
		self.previous_hash = previous_hash
		self.nonce = nonce

	def compute_hash(self):
		fi=inspect.getframeinfo((inspect.stack()[0])[0]); print(">>> ", fi.filename, '; ', fi.function, '(); line:', fi.lineno, file=sys.stderr)
		block_string = json.dumps(self.__dict__, sort_keys=True)
		return sha256(block_string.encode()).hexdigest()

class Blockchain:
	difficulty = 2 # difficulty of PoW algorithm

	def __init__(self):
		fi=inspect.getframeinfo((inspect.stack()[0])[0]); print(">>> ", fi.filename, '; ', fi.function, '(); line:', fi.lineno, file=sys.stderr)
		self.unconfirmed_transactions = []
		self.chain = []

	def create_genesis_block(self):
		fi=inspect.getframeinfo((inspect.stack()[0])[0]); print(">>> ", fi.filename, '; ', fi.function, '(); line:', fi.lineno, file=sys.stderr)
		genesis_block = Block(0, [], 0, "0")
		genesis_block.hash = genesis_block.compute_hash()
		self.chain.append(genesis_block)

	@property
	def last_block(self):
		fi=inspect.getframeinfo((inspect.stack()[0])[0]); print(">>> ", fi.filename, '; ', fi.function, '(); line:', fi.lineno, file=sys.stderr)
		return self.chain[-1]

	def add_block(self, block, proof):
		fi=inspect.getframeinfo((inspect.stack()[0])[0]); print(">>> ", fi.filename, '; ', fi.function, '(); line:', fi.lineno, file=sys.stderr)
		previous_hash = self.last_block.hash
		if previous_hash != block.previous_hash: return False
		if not Blockchain.is_valid_proof(block, proof): return False
		block.hash = proof
		self.chain.append(block)
		return True

	@staticmethod
	def proof_of_work(block):
		fi=inspect.getframeinfo((inspect.stack()[0])[0]); print(">>> ", fi.filename, '; ', fi.function, '(); line:', fi.lineno, file=sys.stderr)
		block.nonce = 0
		computed_hash = block.compute_hash()
		while not computed_hash.startswith('0' * Blockchain.difficulty):
			block.nonce += 1
			computed_hash = block.compute_hash()
		return computed_hash

	def add_new_transaction(self, transaction):
		fi=inspect.getframeinfo((inspect.stack()[0])[0]); print(">>> ", fi.filename, '; ', fi.function, '(); line:', fi.lineno, file=sys.stderr)
		self.unconfirmed_transactions.append(transaction)
		print('Unconfirmed transactions:', self.unconfirmed_transactions, file=sys.stderr)

	@classmethod
	def is_valid_proof(cls, block, block_hash):
		fi=inspect.getframeinfo((inspect.stack()[0])[0]); print(">>> ", fi.filename, '; ', fi.function, '(); line:', fi.lineno, file=sys.stderr)
		# Check if block_hash is valid hash of block and satisfies the difficulty criteria.
		return (block_hash.startswith('0' * Blockchain.difficulty) and block_hash == block.compute_hash())

	@classmethod
	def check_chain_validity(cls, chain):
		fi=inspect.getframeinfo((inspect.stack()[0])[0]); print(">>> ", fi.filename, '; ', fi.function, '(); line:', fi.lineno, file=sys.stderr)
		result = True
		previous_hash = "0"

		for block in chain:
			block_hash = block.hash
			# remove the hash field to recompute the hash again
			# using `compute_hash` method.
			delattr(block, "hash")

			if not cls.is_valid_proof(block, block_hash) or \
              previous_hash != block.previous_hash:
				result = False
				break

			block.hash, previous_hash = block_hash, block_hash

		return result

	def mine(self):
		fi=inspect.getframeinfo((inspect.stack()[0])[0]); print(">>> ", fi.filename, '; ', fi.function, '(); line:', fi.lineno, file=sys.stderr)
		if not self.unconfirmed_transactions: return False
		last_block = self.last_block
		new_block = Block(index=last_block.index + 1, transactions=self.  unconfirmed_transactions, timestamp=time.time(), previous_hash=last_block.hash)
		proof = self.proof_of_work(new_block)
		self.add_block(new_block, proof)
		self.unconfirmed_transactions = []
		return True

app = Flask(__name__)

fi=inspect.getframeinfo((inspect.stack()[0])[0]); print(">>> ", fi.filename, '; ', fi.function, '(); line:', fi.lineno, file=sys.stderr)
# the node's copy of blockchain
blockchain = Blockchain()
blockchain.create_genesis_block()

# the address to other participating members of the network
peers = set()

# Used by to add new data (posts) to the blockchain
@app.route('/new_transaction', methods=['POST'])
def new_transaction():
	fi=inspect.getframeinfo((inspect.stack()[0])[0]); print(">>> ", fi.filename, '; ', fi.function, '(); line:', fi.lineno, file=sys.stderr)
	tx_data = request.get_json()
	print('request:', request, file=sys.stderr)
	print('tx_data:', tx_data, file=sys.stderr)
	required_fields = ["author", "content"]
	for field in required_fields:
		if not tx_data.get(field): return "Invalid transaction data", 404
	tx_data["timestamp"] = time.time()
	blockchain.add_new_transaction(tx_data)
	return "Success", 201

# Returns the node's copy of the chain.
@app.route('/chain', methods=['GET'])
def get_chain():
	fi=inspect.getframeinfo((inspect.stack()[0])[0]); print(">>> ", fi.filename, '; ', fi.function, '(); line:', fi.lineno, file=sys.stderr)
	chain_data = []
	for block in blockchain.chain: chain_data.append(block.__dict__)
	return json.dumps({
	    "length": len(chain_data),
	    "chain": chain_data,
	    "peers": list(peers)})

# Requests the node to mine the unconfirmed transactions (if any).
@app.route('/mine', methods=['GET'])
def mine_unconfirmed_transactions():
	fi=inspect.getframeinfo((inspect.stack()[0])[0]); print(">>> ", fi.filename, '; ', fi.function, '(); line:', fi.lineno, file=sys.stderr)
	result = blockchain.mine()
	if not result: return "No transactions to mine"
	else:
		# Making sure we have the longest chain before announcing to the network
		chain_length = len(blockchain.chain)
		consensus()
		if chain_length == len(blockchain.chain):
			# announce the recently mined block to the network
			announce_new_block(blockchain.last_block)
		return "Block #{} is mined.".format(blockchain.last_block.index)

# endpoint to add new peers to the network.
@app.route('/register_node', methods=['POST'])
def register_new_peers():
	fi=inspect.getframeinfo((inspect.stack()[0])[0]); print(">>> ", fi.filename, '; ', fi.function, '(); line:', fi.lineno)
	node_address = request.get_json()["node_address"]
	if not node_address: return "Invalid data", 400
	peers.add(node_address)
	# Return the consensus blockchain to the newly registered node so that he can sync
	return get_chain()

@app.route('/register_with', methods=['POST'])
def register_with_existing_node():
	fi=inspect.getframeinfo((inspect.stack()[0])[0]); print(">>> ", fi.filename, '; ', fi.function, '(); line:', fi.lineno, file=sys.stderr)
	node_address = request.get_json()["node_address"]
	if not node_address: return "Invalid data", 400
	data = {"node_address": request.host_url}
	headers = {'Content-Type': "application/json"}

	# Make a request to register with remote node and obtain information
	response = requests.post(node_address + "/register_node", data=json.dumps(data), headers=headers)

	if response.status_code == 200:
		global blockchain
		global peers
		# update chain and the peers
		chain_dump = response.json()['chain']
		blockchain = create_chain_from_dump(chain_dump)
		peers.update(response.json()['peers'])
		return "Registration successful", 200
	else: 	return response.content, response.status_code

def create_chain_from_dump(chain_dump):
	fi=inspect.getframeinfo((inspect.stack()[0])[0]); print(">>> ", fi.filename, '; ', fi.function, '(); line:', fi.lineno, file=sys.stderr)
	generated_blockchain = Blockchain()
	generated_blockchain.create_genesis_block()
	for idx, block_data in enumerate(chain_dump):
		if idx == 0: continue  # skip genesis block
		block = Block(block_data["index"], block_data["transactions"], block_data["timestamp"], block_data["previous_hash"], block_data["nonce"])
		proof = block_data['hash']
		added = generated_blockchain.add_block(block, proof)
		if not added: raise Exception("The chain dump is tampered!!")
	return generated_blockchain

# Verifies and adds a block mined by someone else to the node's chain.
@app.route('/add_block', methods=['POST'])
def verify_and_add_block():
	fi=inspect.getframeinfo((inspect.stack()[0])[0]); print(">>> ", fi.filename, '; ', fi.function, '(); line:', fi.lineno, file=sys.stderr)
	block_data = request.get_json()
	block = Block(block_data["index"], block_data["transactions"], block_data["timestamp"], block_data["previous_hash"], block_data["nonce"])
	proof = block_data['hash']
	added = blockchain.add_block(block, proof)
	if not added: return "The block was discarded by the node", 400
	return "Block added to the chain", 201

# Query unconfirmed transactions
@app.route('/pending_tx')
def get_pending_tx():
	fi=inspect.getframeinfo((inspect.stack()[0])[0]); print(">>> ", fi.filename, '; ', fi.function, '(); line:', fi.lineno, file=sys.stderr)
	return json.dumps(blockchain.unconfirmed_transactions)

def consensus():
	fi=inspect.getframeinfo((inspect.stack()[0])[0]); print(">>> ", fi.filename, '; ', fi.function, '(); line:', fi.lineno, file=sys.stderr)
	global blockchain
	longest_chain = None
	current_len = len(blockchain.chain)
	for node in peers:
		response = requests.get('{}chain'.format(node))
		length = response.json()['length']
		chain = response.json()['chain']
		if length > current_len and blockchain.check_chain_validity(chain):
			current_len = length
			longest_chain = chain
	if longest_chain:
		blockchain = longest_chain
		return True
	return False

def announce_new_block(block):
	fi=inspect.getframeinfo((inspect.stack()[0])[0]); print(">>> ", fi.filename, '; ', fi.function, '(); line:', fi.lineno, file=sys.stderr)
	for peer in peers:
		url = "{}add_block".format(peer)
		headers = {'Content-Type': "application/json"}
		requests.post(url, data=json.dumps(block.__dict__, sort_keys=True), headers=headers)

# Uncomment this line if you want to specify the port number in the code
app.run(debug=True, port=80)
