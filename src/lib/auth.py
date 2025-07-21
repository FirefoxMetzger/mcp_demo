from mcp.server.auth.provider import TokenVerifier
from mcp.server.auth.provider import AccessToken
from mcp.server.auth.settings import AuthSettings
from pathlib import Path
import datetime
from typing import Any

import jwt

DOMAIN = "https://awesome-mcp.com"
PUBLIC_KEY = (Path(__file__).parents[1] / "static" / "public_key.pem").read_text()

ALLOWED_ORIGINS = ["http://localhost:6274"]


def generate_token(domain: str, client_id: str, lifetime: int, kid: str = "1") -> str:
    now = datetime.datetime.now(datetime.timezone.utc)
    payload = {
        "iss": f"https://{domain}",
        "sub": client_id,
        "aud": f"{domain}/mcp",
        "iat": now,
        "exp": now + datetime.timedelta(seconds=lifetime),
        "scope": "mcp:full_access",
    }

    private_key = (Path(__file__).parents[1] / "static" / "private_key.pem").read_bytes()
    return jwt.encode(payload, private_key, algorithm="RS256", headers={"kid": "1"})

def verify_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token, PUBLIC_KEY, algorithms=["RS256"], audience=f"{DOMAIN}/mcp"
        )
    except jwt.PyJWTError as e:
        raise AssertionError("Failed to decrypt token") from e

    assert payload["iss"] == f"https://{DOMAIN}", f"Invalid issuer: {payload['iss']}"
    assert payload["scope"] == "mcp:full_access", f"Invalid scope: {payload['scope']}"

    return payload

