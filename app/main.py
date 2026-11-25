from fastapi import FastAPI

from app.options import router as option_router
from app.orders import router as order_router
from app.storage import MemoryStore


def create_app(store: MemoryStore | None = None) -> FastAPI:
    """App factory allows each test to have independent data."""
    app = FastAPI(
        title="CampusPrint CRUD & Integration Testing Demo",
        description="Two backend features, full CRUD lifecycle, automatic API tests. Demo identity only.",
        version="1.0.0",
    )
    app.state.store = store if store is not None else MemoryStore.seeded()
    app.include_router(option_router)
    app.include_router(order_router)

    @app.get("/health", tags=["Health"])
    def health():
        return {"status": "ok"}

    return app


app = create_app()
