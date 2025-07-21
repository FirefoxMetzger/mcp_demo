from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
import base64
from pathlib import Path

# Load your private key
private_key = (Path(__file__).parent / "src" / "static" / "private_key.pem").read_bytes()
private_key = serialization.load_pem_private_key(private_key, password=None, backend=default_backend())

public_key = private_key.public_key()
numbers = public_key.public_numbers()

n = base64.urlsafe_b64encode(numbers.n.to_bytes((numbers.n.bit_length() + 7) // 8, 'big')).rstrip(b'=').decode('utf-8')
e = base64.urlsafe_b64encode(numbers.e.to_bytes((numbers.e.bit_length() + 7) // 8, 'big')).rstrip(b'=').decode('utf-8')

print("n:", n)
print("e:", e)
