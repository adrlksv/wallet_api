import uvicorn

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from contextlib import asynccontextmanager

from app.db.db_helper import db_helper
from app.core.config import settings
from app.api.api_v1.routers.wallet import router as wallet_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    
    await db_helper.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        debug=True,
        docs_url="/api/docs",
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
    )
    
    app.include_router(wallet_router)
    
    return app


if __name__ == "__main__":
    uvicorn.run(
        factory=create_app,
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )
