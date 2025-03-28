from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.middleware.cors import CORSMiddleware
from utils.responses import json_response

from api import router
import redis.asyncio as redis

app = FastAPI(
    title="GoSend API",
    description="GoSend+ API Documentation",
    version="0.1.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)

# ✅ Initialize Redis globally
redis_client: redis.Redis | None = None

@app.on_event("startup")
async def startup():
    """Initialize Redis connection on startup."""
    global redis_client
    try:
        redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)
        await redis_client.ping()  # Test connection
        print("✅ Connected to Redis successfully!")
    except Exception as e:
        print(f"❌ Redis connection error: {e}")

@app.on_event("shutdown")
async def shutdown():
    """Close Redis connection on shutdown."""
    global redis_client
    if redis_client:
        await redis_client.close()
        print("🔌 Redis connection closed.")

# ✅ Exception Handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc: StarletteHTTPException):
    return json_response(
        message=str(exc.detail),
        status_code=exc.status_code
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    return json_response(
        message="Validation error occurred",
        data={"errors": exc.errors()},
        status_code=400
    )

@app.get("/")
async def root():
    return {"message": "Hello World"}

# ✅ Test Redis Connection
@app.get("/test-redis")
async def test_redis():
    """Test if Redis is working."""
    if not redis_client:
        return {"error": "Redis is not connected"}
    
    await redis_client.set("test_key", "Hello from Redis!")
    value = await redis_client.get("test_key")
    return {"redis_message": value}
