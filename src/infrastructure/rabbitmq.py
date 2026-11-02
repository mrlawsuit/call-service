import asyncio
import logging
from contextlib import suppress

import aio_pika
from pydantic import ValidationError

from src.application.use_cases.save_call_event import SaveCallEventUseCase
from src.domain.models import CallEvent

logger = logging.getLogger(__name__)


class RabbitMQConsumer:
    def __init__(
        self,
        save_call: SaveCallEventUseCase,
        rabbitmq_url: str,
        queue_name: str,
    ) -> None:
        self._save_call = save_call
        self._rabbitmq_url = rabbitmq_url
        self._queue_name = queue_name
        self._task: asyncio.Task[None] | None = None

    def start(self) -> None:
        if self._task is not None:
            raise RuntimeError("Консюмер уже хапущен")

        self._task = asyncio.create_task(
            self._run(),
            name="rabbitmq-consumer",
        )

    async def stop(self) -> None:
        if self._task is None:
            return

        task = self._task
        task.cancel()

        try:
            with suppress(asyncio.CancelledError):
                await task
        finally:
            self._task = None

        logger.info("Консюмер остановлен")

    async def _run(self) -> None:
        while True:
            try:
                connection = await aio_pika.connect_robust(
                    self._rabbitmq_url,
                    timeout=10,
                )

                async with connection:
                    channel = await connection.channel()

                    await channel.set_qos(prefetch_count=1)

                    queue = await channel.declare_queue(
                        self._queue_name,
                        durable=True,
                    )

                    logger.info(
                        "Очередь=%s",
                        self._queue_name,
                    )

                    async with queue.iterator() as iterator:
                        async for message in iterator:
                            await self._handle_message(message)

            except asyncio.CancelledError:
                raise

            except Exception:
                logger.exception(
                    "RabbitMQConsumer, упал, перезапуск через 3 секунды..."
                )
                await asyncio.sleep(3)

    async def _handle_message(
        self,
        message: aio_pika.abc.AbstractIncomingMessage,
    ) -> None:
        try:
            event = CallEvent.model_validate_json(message.body)

        except ValidationError as exc:
            logger.warning(
                "Ошибка: %s",
                exc.errors(include_input=False),
            )
            await message.reject(requeue=False)
            return

        try:
            await self._save_call.execute(event)

        except asyncio.CancelledError:
            raise

        except Exception:
            logger.exception(
                "Не можем сохранить! call_id=%s",
                event.call.call_id,
            )

            await asyncio.sleep(2)
            await message.nack(requeue=True)
            return

        await message.ack()

        logger.info(
            "Сохранен call_id=%s campaign_id=%s",
            event.call.call_id,
            event.call.campaign_id,
        )
