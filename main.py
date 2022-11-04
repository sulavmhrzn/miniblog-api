from fastapi import FastAPI

from routers import ping, users
from settings import settings

api = FastAPI(title="Mini blog API", description="An API for a simple blogging system")
api.include_router(users.router)
api.include_router(ping.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:api", reload=settings.DEBUG)
