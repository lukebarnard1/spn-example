

# S-Box for x, a 4 bit integer
def sbox(x):
	return [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0][x]

def inv_sbox(x):
	return [15, 1, 6, 12, 0, 14, 5, 11, 3, 10, 13, 7, 9, 4, 2, 8][x]

permutation = [1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15, 4, 8, 12, 16]

# 0-indexed
permutation = [x - 1 for x in permutation]

inv_permutation = [permutation.index(i) for i in range(len(permutation))]

def substitutions(state):
	return [sbox(x) for x in state]

def inverse_substitutions(state):
	return [inv_sbox(x) for x in state]

# where state consists of a series of 4, 4 bit integers
def perm(state, perm_desc):
	next_state = [0, 0, 0, 0]

	for j in range(4):
		for i in range(4):
			k = state[j]
			if k << i & 8: # ith lowest bit true
				p = perm_desc[j * 4 + i]

				s = p % 4
				next_state_index = (p - s) / 4
				
				next_state[next_state_index] |= 8 >> s

	return next_state

def permute(state):
	return perm(state, permutation)

def inv_permute(state):
	return perm(state, inv_permutation)

def xor(state, key):
	return [x ^ k for (x,k) in zip(state, key)]

# k is [1,2,3,..,16]
def gen_keys(k, rounds):
	if rounds < len(k) - 2:
		return [k[i:i+4] for i in range(rounds)]
	else:
		return []

def encrypt(plaintext, keys):
	state = plaintext

	# key is [1, 4, 3, 5]
	for key in keys[:-2]:
		state = xor(state, key)
		state = substitutions(state)
		state = permute(state)

	state = xor(state, keys[-2])
	state = substitutions(state)

	return xor(state, keys[-1])

def decrypt(ciphertext, keys):
	keys = [k for k in reversed(keys)]

	state = ciphertext
	
	state = xor(state, keys[0])
	state = inverse_substitutions(state)
	state = xor(state, keys[1])

	for key in keys[2:]:
		state = permute(state)
		state = inverse_substitutions(state)
		state = xor(state, key)

	return state

def decrypt_simple(ciphertext, keys):
	'''This function uses the existing encryption algorithm but
	alters the keys in order to decrypt the ciphertext.
	'''
	# Modify the keys:
	modified_keys = []

	for i,k in enumerate(keys):
		if i == 0 or i == len(keys) - 1:
			modified_keys.append(k)
		else:
			modified_keys.append(inv_permute(k))

	# Also reverse the keys
	modified_keys = [k for k in reversed(modified_keys)]

	print 'modified_keys = {0}'.format([hexify(k) for k in modified_keys])

	return encrypt(ciphertext, modified_keys)


def hexify(t):
	return ''.join(['{0:#X}'.format(c)[2:] for c in t])

def test(plaintext, keys, decrypt_func):
	hex_keys = [hexify(k) for k in keys]

	print '\nRunning test with x = {0}, k = {1}'.format(hexify(plaintext), hex_keys)
	ciphertext = encrypt(plaintext, keys)
	actual_plaintext = decrypt_func(ciphertext, keys)


	if plaintext == actual_plaintext:
		print 'Test passed with x = {0}, k = {1}'.format(hexify(plaintext), hex_keys)
	else:
		print 'Test failed with x = {0}, k = {1}'.format(hexify(plaintext), hex_keys)
		print 'actual_plaintext = {0}'.format(hexify(actual_plaintext))

if __name__ == '__main__':
	for decrypt_func in [decrypt, decrypt_simple]:
		# From the CM30173 lecture slides:
		test([4, 14, 10, 1], gen_keys([14, 7, 6, 7, 9, 0, 3, 13], 5), decrypt_func)

		# Other, random test
		# test([1, 2, 3, 4], gen_keys([9, 2, 4, 12, 14, 9, 14, 3, 4, 15, 2], 8), decrypt_func)

