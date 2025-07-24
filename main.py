import logging
from ratelimit import RateLimitMiddleware, Rule
from ratelimit.backends.simple import MemoryBackend
from src.lib.auth import ratelimit_auth_function

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
    "192.168.65.1",
    "10.0.0.230"
]

# TODO: Validate the origin of the request
app = riddles_mcp.streamable_http_app()
app.mount("", auth_server)
app.add_middleware(RateLimitMiddleware, ratelimit_auth_function, MemoryBackend(), {
    "/mcp": [Rule(second=10, minute=20), Rule(second=10, minute=60, group="authenticated")],
    r".*": [Rule(second=10, minute=20), Rule(second=10, minute=60, group="authenticated")]
})
# app.add_middleware(IPWhitelistMiddleware, allowed_ips=allowed_ips)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)