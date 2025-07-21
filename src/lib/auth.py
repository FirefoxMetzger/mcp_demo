import datetime
from pathlib import Path
from typing import Any

import jwt
from starlette.types import Scope

DOMAIN = "https://awesome-mcp.com"
PUBLIC_KEY = (Path(__file__).parents[1] / "static" / "public_key.pem").read_text()


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

    private_key = (
        Path(__file__).parents[1] / "static" / "private_key.pem"
    ).read_bytes()
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


async def ratelimit_auth_function(scope: Scope):
    """
    Find the user id for rate limiting. We try the following order:
        - get the client ID from the JWT
        - use the client's IP address
    """

    for header_name, header_value in scope["headers"]:
        if header_name.lower() == b"authorization":
            token = header_value.decode("utf-8")
            break
    else:
        return scope["client"][0], "default"

    try:
        assert token.startswith("Bearer ")
        payload = verify_token(token[7:])
        assert "sub" in payload
    except AssertionError:
        return scope["client"][0], "default"

    return payload["sub"], "authenticated"
