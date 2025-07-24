from starlette.applications import Starlette
from starlette.routing import Route

import logging
from pathlib import Path

from starlette.applications import Starlette
from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import JSONResponse

import base64
import json

from ..lib.auth import generate_token


DOMAIN = "https://awesome-mcp.com"
KNOWN_CLIENTS = {
    "elevenlabs-agent": "super-secret-key",
}
JWKS = json.loads((Path(__file__).parents[1] / "static" / "jwks.json").read_text())


def oauth_authorization_server(request: Request) -> str:
    """Authentication server metadata.

    This JSON contains information about the capabilities of the authentication
    server and what to do to get an access token. You would find this on any
    server that can grant access tokens.

    Note: You can find both `oauth_protected_source` and
    `oauth_authorization_server` in this example because this server hosts both
    the protected resource and the authentication server. In other words, it
    manges its own access tokens.

    """
    return JSONResponse(
        {
            "issuer": f"https://{DOMAIN}",
            "token_endpoint": f"https://{DOMAIN}/token",
            "grant_types_supported": ["client_credentials"],
            "scopes_supported": ["mcp:full_access"],
            "token_endpoint_auth_methods_supported": ["client_secret_basic"],
            "jwks_uri": f"https://{DOMAIN}/.well-known/jwks",
        }
    )


async def get_token(request: Request) -> str:
    """Hand out access tokens to validated clients by issuing a signed JWT."""

    form_data = await request.form()

    try:
        assert form_data.get("grant_type") is not None, "Missing grant type"
        assert (
            form_data["grant_type"] == "client_credentials"
        ), f"Invalid grant type: {form_data['grant_type']}"

        if "scope" in form_data:
            assert (
                "mcp:full_access" in form_data["scope"].split()
            ), f"No supported scope: {form_data['scope']}"

        assert (
            request.headers.get("Authorization") is not None
        ), "Missing authorization header"
        assert request.headers["Authorization"].startswith(
            "Basic "
        ), "Invalid authorization header"

        b64_credentials = request.headers["Authorization"][6:]
        try:
            decoded = base64.b64decode(b64_credentials).decode("utf-8")
        except base64.binascii.Error as e:
            raise AssertionError("Invalid base64 encoding")

        assert ":" in decoded, "Invalid credentials."
        client_id, client_secret = decoded.split(":", 1)
        assert client_id in KNOWN_CLIENTS, f"Invalid credentials."
        assert client_secret == KNOWN_CLIENTS[client_id], f"Invalid credentials."

    except AssertionError as e:
        msg = str(e)
        if msg == "Invalid credentials.":
            return_code = 401
        else:
            return_code = 400

        return JSONResponse(
            {
                "error": "invalid_request",
                "error_description": str(e),
            },
            status_code=return_code,
        )

    return JSONResponse(
        {
            "access_token": generate_token(DOMAIN, client_id, 3600),
            "token_type": "Bearer",
            "expires_in": 3600,
        }
    )


def get_jwks(request: Request) -> JSONResponse:
    return JSONResponse(JWKS)


auth_server = Starlette(
    routes=[
        Route("/.well-known/jwks", get_jwks),
        Route("/.well-known/oauth-authorization-server", oauth_authorization_server),
        Route("/token", get_token, methods=["POST"]),
    ],
)
