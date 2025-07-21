from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

class IPWhitelistMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, allowed_ips):
        super().__init__(app)
        self.allowed_ips = allowed_ips

    async def dispatch(self, request, call_next):
        client_ip = request.client.host
        if client_ip not in self.allowed_ips:
            return JSONResponse({"error": "Forbidden"}, status_code=403)
        return await call_next(request)
