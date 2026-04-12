import logging
from fastapi import FastAPI
from src.api.routes import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("kubesentient")

def create_app() -> FastAPI:
    """Factory function to create the FastAPI application."""
    app = FastAPI(
        title="KubeSentient Agent API",
        description="Autonomous SRE Agent Interface",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Include routers
    app.include_router(router, prefix="/api/v1")

    @app.get("/health")
    async def health_check():
        """K8s liveness/readiness probe endpoint."""
        return {"status": "ok", "version": "0.1.0"}

    return app

app = create_app()
