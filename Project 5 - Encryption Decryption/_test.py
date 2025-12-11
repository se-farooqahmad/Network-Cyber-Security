import pytest
from crypto.rsa import RSA

from test_data import public_key, private_key, encrypt, decrypt, encrypt_decrypt, sign, verify

pytestmark = pytest.mark.timeout(1)

@pytest.mark.parametrize("bit_length, p, q, expected_public_key", public_key.test_data)
def test_generate_public_key(bit_length, p, q, expected_public_key):

    p = int(p, 16)
    q = int(q, 16)

    rsa = RSA(prime_bit_length=bit_length)
    rsa.set_primes(p, q)
    public_key = rsa.generate_public_key()
    assert public_key == expected_public_key

@pytest.mark.parametrize("bit_length, p, q, expected_private_key", private_key.test_data)
def test_generate_private_key(bit_length, p, q, expected_private_key):

    p = int(p, 16)
    q = int(q, 16)

    rsa = RSA(prime_bit_length=bit_length)
    rsa.set_primes(p, q)
    public_key = rsa.generate_private_key()
    assert public_key == expected_private_key

@pytest.mark.parametrize("p, q, msg, ciphertext", encrypt.test_data)
def test_encrypt(p, q, msg, ciphertext):

    p = int(p, 16)
    q = int(q, 16)

    rsa = RSA(prime_bit_length=512)
    rsa.set_primes(p, q)
    rsa.generate_public_key()
    rsa.generate_private_key()

    assert rsa.encrypt(msg) == ciphertext

@pytest.mark.parametrize("p, q, msg, ciphertext", decrypt.test_data)
def test_decrypt(p, q, msg, ciphertext):

    p = int(p, 16)
    q = int(q, 16)

    rsa = RSA(prime_bit_length=256)
    rsa.set_primes(p, q)
    rsa.generate_public_key()
    rsa.generate_private_key()

    assert rsa.decrypt(ciphertext) == msg

@pytest.mark.parametrize("message", encrypt_decrypt.test_data)
def test_encrypt_decrypt(message):
    rsa = RSA(prime_bit_length=512)
    rsa.generate_primes()
    rsa.generate_public_key()
    rsa.generate_private_key()

    assert rsa.decrypt(rsa.encrypt(message)) == message

@pytest.mark.parametrize("p, q, message, signature", sign.test_data)
def test_sign(p, q, message, signature):

    p = int(p, 16)
    q = int(q, 16)    

    rsa = RSA(prime_bit_length=256)
    rsa.set_primes(p, q)
    rsa.generate_public_key()
    rsa.generate_private_key()

    assert rsa.sign(message) == signature

@pytest.mark.parametrize("message", verify.test_data)
def test_verify_signature(message):
    rsa = RSA(prime_bit_length=512)
    rsa.generate_primes()
    rsa.generate_public_key()
    rsa.generate_private_key()

    signature = rsa.sign(message)
    assert rsa.verify_signature(message, signature) == True