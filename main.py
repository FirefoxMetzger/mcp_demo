from ratelimit import RateLimitMiddleware, Rule
from ratelimit.backends.simple import MemoryBackend
from src.lib.auth import ratelimit_auth_function

from src.services.authorization_server import auth_server
from src.services.riddle_mcp import riddles_mcp

app = riddles_mcp.streamable_http_app()
app.mount("", auth_server)
app.add_middleware(RateLimitMiddleware, ratelimit_auth_function, MemoryBackend(), {
    r".*": [Rule(second=10, minute=20), Rule(second=10, minute=60, group="authenticated")]
})
