# main.py

from fastapi import FastAPI, Depends
from database.db import Base, engine
from routes.contacts import router as contacts_router
from routes.auth import router as auth_router
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from config import settings
import aioredis
from fastapi.middleware.cors import CORSMiddleware
from aioredis.exceptions import RedisError
from routes.users import router as users_router
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(users_router, prefix='/api/users')
app.include_router(contacts_router, prefix="/contacts", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
app.include_router(auth_router, prefix="/auth", dependencies=[Depends(RateLimiter(times=10, seconds=60))])

@app.on_event("startup")
async def startup():
    try:
        redis_pool = await aioredis.from_url(settings.REDIS_URL)
        await FastAPILimiter.init(redis_pool)
    except RedisError as e:
        raise Exception(f"Failed to connect to Redis: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
