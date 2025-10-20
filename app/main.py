import uvicorn

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from contextlib import asynccontextmanager

from app.db.db_helper import db_helper
from app.core.config import settings


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
    
    return app


if __name__ == "__main__":
    uvicorn.run(
        factory=create_app,
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )
