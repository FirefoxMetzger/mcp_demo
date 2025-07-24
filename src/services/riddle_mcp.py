from mcp.server.fastmcp import FastMCP
from mcp.server.auth.provider import TokenVerifier
from mcp.server.auth.provider import AccessToken
from mcp.server.auth.settings import AuthSettings
from mcp.server.fastmcp import Context
from random import randint
import os
import logging
import json
from pathlib import Path
from ..lib.auth import verify_token
from ..lib.session_storage import IPDB

DOMAIN = os.getenv("domain")
RIDDLES = json.loads(
    (Path(__file__).parents[1] / "static" / "riddles.json").read_text()
)

logger = logging.getLogger(__name__)


class APIKeyValidation(TokenVerifier):
    async def verify_token(self, token: str) -> AccessToken | None:
        try:
            payload = verify_token(token)
        except AssertionError as e:
            logger.warning(f"JWT verification failed: {e}")
            return None

        return AccessToken(
            token=token,
            client_id=payload["sub"],
            scopes=payload.get("scope").split(),
        )


session_store = IPDB(lifetime=300)
riddles_mcp = FastMCP(
    "Riddle MCP",
    token_verifier=APIKeyValidation(),
    auth=AuthSettings(
        issuer_url=f"https://{DOMAIN}",
        resource_server_url=f"https://{DOMAIN}/mcp",
        required_scopes=["mcp:full_access"],
    ),
)


@riddles_mcp.tool(
    name="get_riddle",
    description="This tool is used when the user indicates they"
    " are ready to solve the riddle. It returns the riddle they have to solve",
    structured_output=True,
)
def get_riddle(ctx: Context) -> str:
    """Return a random riddle."""

    session_id = ctx.request_context.request.headers["mcp-session-id"]

    riddle_id = randint(0, len(RIDDLES) - 1)
    riddle = RIDDLES[riddle_id]

    session_store[session_id] = riddle
    return riddle["riddle"]


@riddles_mcp.tool(
    name="validate_riddle_answer",
    description="This tool is used after the user provides an answer to check if it solves the riddle.",
    structured_output=True,
)
def validate_riddle_answer(answer: str, ctx: Context) -> str:
    """True if the answer solves the riddle, False otherwise."""

    session_id = ctx.request_context.request.headers["mcp-session-id"]

    try:
        riddle_data = session_store[session_id]
    except KeyError:
        logger.warning(f"No riddle found for session {session_id}")
        return "No riddle has been given yet."

    if answer.lower() == riddle_data["answer"].lower():
        return "The answer is correct!"
