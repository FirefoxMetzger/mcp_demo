import logging

from src.lib.ip_whitelist import IPWhitelistMiddleware
from src.services.authorization_server import auth_server
from src.services.riddle_mcp import riddles_mcp


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Elevenlabs IP addresses
# source: https://elevenlabs.io/docs/conversational-ai/workflows/post-call-webhooks#ip-whitelisting
allowed_ips = [
    "34.67.146.145", 
    "34.59.11.47",
    "127.0.0.1",
]

# TODO: Validate the origin of the request
# TODO: Rate limiting


app = riddles_mcp.streamable_http_app()
app.mount("", auth_server)
app.add_middleware(IPWhitelistMiddleware, allowed_ips=allowed_ips)
