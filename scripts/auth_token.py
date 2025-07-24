"""
This script generates an access token for the MCP server. The token is valid
for 90 days. The script also generates the jwks.json that the authorization server
will serve so that clients and resource servers can verify the token.
"""

import datetime
from pathlib import Path

import jwt
import os
import json

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import base64


DOMAIN = os.getenv("domain")
PRIVATE_KEY_PATH = Path(__file__).parents[1] / "private_token_key.pem"
PUBLIC_KEY_PATH = Path(__file__).parents[1] / "src" / "static" / "public_token_key.pem"
API_KEY_FILE = Path(__file__).parents[1] / "auth_token.txt"
JWK_FILE = Path(__file__).parents[1] / "src" / "static" / "jwks.json"
KEY_ID = "1"


# Convert to base64url
def int_to_base64url(value):
    # Convert integer to big-endian bytes
    byte_length = (value.bit_length() + 7) // 8
    value_bytes = value.to_bytes(byte_length, byteorder="big")
    # Base64url encode (no padding)
    return base64.urlsafe_b64encode(value_bytes).rstrip(b"=").decode("ascii")


now = datetime.datetime.now(datetime.timezone.utc)
payload = {
    "iss": f"https://{DOMAIN}",
    "sub": "elevenlabs-agent",
    "aud": f"https://{DOMAIN}/mcp",
    "iat": now,
    "exp": now + datetime.timedelta(days=90),
    "scope": "mcp:full_access",
}


# Generate private key
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,  # or 4096 for more security
)
PRIVATE_KEY_PATH.write_bytes(
    private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),  # or use BestAvailableEncryption(b"password")
    )
)

# generate the access token (API key)
token = jwt.encode(payload, private_key, algorithm="RS256", headers={"kid": KEY_ID})
API_KEY_FILE.write_text(token)

# Generate public key
public_key = private_key.public_key()
PUBLIC_KEY_PATH.write_bytes(
    public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
)
numbers = public_key.public_numbers()
n = (
    base64.urlsafe_b64encode(
        numbers.n.to_bytes((numbers.n.bit_length() + 7) // 8, "big")
    )
    .rstrip(b"=")
    .decode("utf-8")
)
e = (
    base64.urlsafe_b64encode(
        numbers.e.to_bytes((numbers.e.bit_length() + 7) // 8, "big")
    )
    .rstrip(b"=")
    .decode("utf-8")
)



jwk = {
    "kty": "RSA",
    "use": "sig",
    "key_ops": ["verify"],
    "alg": "RS256",
    "kid": KEY_ID,
    "n": int_to_base64url(numbers.n),
    "e": int_to_base64url(numbers.e),
}
JWK_FILE.write_text(json.dumps({"keys": jwk}))
