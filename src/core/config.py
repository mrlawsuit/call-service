import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_database: str = "call_service"
    rabbitmq_url: str = "amqp://calls_user:calls_password@localhost:5672/"
    rabbitmq_queue: str = "call_results"

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            mongodb_uri=os.getenv("MONGODB_URI", cls.mongodb_uri),
            mongodb_database=os.getenv("MONGODB_DATABASE", cls.mongodb_database),
            rabbitmq_url=os.getenv("RABBITMQ_URL", cls.rabbitmq_url),
            rabbitmq_queue=os.getenv("RABBITMQ_QUEUE", cls.rabbitmq_queue),
        )
