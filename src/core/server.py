import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pymongo import AsyncMongoClient

from src.application.use_cases.save_call_event import SaveCallEventUseCase
from src.core.api.routers import router as api_v1_router
from src.core.config import Settings
from src.core.containers import build_container
from src.infrastructure.mongodb import setup_database
from src.infrastructure.rabbitmq import RabbitMQConsumer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

logger = logging.getLogger(__name__)


def init_routers(app: FastAPI) -> None:
    app.include_router(api_v1_router)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = Settings.from_env()

    client = AsyncMongoClient(
        settings.mongodb_uri,
        tz_aware=True,
        serverSelectionTimeoutMS=10000,
    )

    consumer = None

    try:
        db = client[settings.mongodb_database]
        await setup_database(db)

        container = build_container(db)
        app.state.container = container

        consumer = RabbitMQConsumer(
            save_call=container.resolve(SaveCallEventUseCase),
            rabbitmq_url=settings.rabbitmq_url,
            queue_name=settings.rabbitmq_queue,
        )

        consumer.start()

        yield
    finally:
        if consumer is not None:
            await consumer.stop()

        await client.close()


def create_app() -> FastAPI:
    _app = FastAPI(
        title="Call-Service Backend",
        version="1.0.0",
        description="Сервис обработки звонков",
        lifespan=lifespan,
    )

    init_routers(_app)

    return _app
