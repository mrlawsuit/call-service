"""Публикует 4 события звонков в RabbitMQ через AMQP и проверяет результат API."""

import asyncio
import json
import os
import time
from urllib.error import URLError
from urllib.request import urlopen

import aio_pika

RABBITMQ_URL = os.getenv(
    "RABBITMQ_URL", "amqp://calls_user:calls_password@localhost:5672/"
)
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "call_results")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")
API_PREFIX = os.getenv("API_PREFIX", "/v1").rstrip("/")

CAMPAIGNS = [
    {
        "campaign_id": "camp_001",
        "name": "Напоминание о платеже",
        "created_at": "2026-10-20T10:00:00Z",
    },
    {
        "campaign_id": "camp_002",
        "name": "Оценка качества обслуживания",
        "created_at": "2026-10-20T11:00:00Z",
    },
]

CALLS = [
    {
        "call_id": "call_0001",
        "campaign_id": "camp_001",
        "phone": "79001234567",
        "status": "success",
        "created_at": "2026-10-20T10:06:00Z",
    },
    {
        "call_id": "call_0002",
        "campaign_id": "camp_001",
        "phone": "79001234568",
        "status": "failed",
        "created_at": "2026-10-20T10:07:00Z",
    },
    {
        "call_id": "call_0003",
        "campaign_id": "camp_002",
        "phone": "79001234569",
        "status": "success",
        "created_at": "2026-10-20T11:06:00Z",
    },
    {
        "call_id": "call_0004",
        "campaign_id": "camp_002",
        "phone": "79001234570",
        "status": "success",
        "created_at": "2026-10-20T11:07:00Z",
    },
]


async def publish_calls() -> None:
    for attempt in range(1, 21):
        try:
            connection = await aio_pika.connect_robust(RABBITMQ_URL, timeout=5)
            break
        except Exception as exc:
            if attempt == 20:
                raise RuntimeError("Не удалось подключиться к RabbitMQ") from exc
            await asyncio.sleep(1)

    async with connection:
        channel = await connection.channel(
            publisher_confirms=True,
            on_return_raises=True,
        )
        await channel.declare_queue(RABBITMQ_QUEUE, durable=True)

        campaigns_by_id = {item["campaign_id"]: item for item in CAMPAIGNS}

        for call in CALLS:
            event = {
                "campaign": campaigns_by_id[call["campaign_id"]],
                "call": call,
            }
            message = aio_pika.Message(
                body=json.dumps(event, ensure_ascii=False).encode("utf-8"),
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                message_id=call["call_id"],
            )
            await channel.default_exchange.publish(
                message,
                routing_key=RABBITMQ_QUEUE,
                mandatory=True,
            )
            print(f"Published: {call['call_id']} -> {call['campaign_id']}")


def wait_for_calls(timeout: float = 40.0) -> None:
    """Ожидает, пока API вернёт два звонка для каждой кампании."""
    expected = {
        campaign["campaign_id"]: {
            call["call_id"]
            for call in CALLS
            if call["campaign_id"] == campaign["campaign_id"]
        }
        for campaign in CAMPAIGNS
    }

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            ready = True
            for campaign_id, call_ids in expected.items():
                with urlopen(
                    f"{API_BASE_URL}{API_PREFIX}/campaigns/{campaign_id}/calls",
                    timeout=3,
                ) as response:
                    calls = json.load(response)

                if (
                    not isinstance(calls, list)
                    or len(calls) != len(call_ids)
                    or {item["call_id"] for item in calls} != call_ids
                ):
                    ready = False
                    break

            if ready:
                return
        except (URLError, TimeoutError, ValueError, KeyError):
            pass

        time.sleep(0.5)

    raise RuntimeError("API не вернул 4 сохранённых звонка за 40 секунд")


def main() -> None:
    asyncio.run(publish_calls())
    wait_for_calls()
    print("Успешно: у каждой кампании по 2 звонка")
    print(f"GET {API_BASE_URL}{API_PREFIX}/campaigns/camp_001/calls")


if __name__ == "__main__":
    main()
