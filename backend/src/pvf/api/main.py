from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pvf.api.routes import asks, bids, dashboard, locations, specs, trades
from pvf.config import get_settings


def create_app() -> FastAPI:
    app = FastAPI(title="PVF Marketplace API", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[get_settings().web_url],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    for module in (specs, locations, asks, bids, trades, dashboard):
        app.include_router(module.router, prefix="/v1")

    @app.get("/health", tags=["ops"])
    def health():
        return {"status": "ok"}

    return app


app = create_app()
