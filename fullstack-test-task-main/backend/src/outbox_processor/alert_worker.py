import math
import aio_pika
import pydantic_core
from sqlalchemy.exc import SQLAlchemyError
from src.infrastructure.db.sessions import get_async_session
from src.infrastructure.broker.rabbitmq import rabbit_connector
from aio_pika import Message, DeliveryMode
import asyncio
import logging
from src.infrastructure.config import settings
from src.outbox_processor.queries.outboxQueries import send_alert, change_status
from src.schemas.messagesSchemas import FilePayload

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=settings.log_level.upper(),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


def generate_ttl(retry_count):
    ttl = int(math.exp(retry_count + 1) * 1000)
    return ttl


async def main():
    async def publish_status_failed(body: bytes, retry_count: int, error: str):
        await channel.default_exchange.publish(
            Message(
                body=body,
                headers={
                    "x-retry-count": retry_count,
                    "x-error": error,
                },
                delivery_mode=DeliveryMode.PERSISTENT,
            ),
            routing_key="alert_failed",
        )

    async def publish_status_retry(body: bytes, retry_count: int, delay: int):
        await channel.default_exchange.publish(
            Message(
                body=body,
                headers={
                    "x-retry-count": retry_count,
                },
                expiration=delay,
                delivery_mode=DeliveryMode.PERSISTENT,
            ),
            routing_key="alert_retry",
        )

    async def callback_with_retry(message: aio_pika.IncomingMessage):
        async with message.process(ignore_processed=True):
            logger.info("Alert_worker - message received")
            headers = message.headers or {}
            retry_count = headers.get("x-retry-count", 0)

            max_retries = settings.retry_count
            body = message.body
            logger.info(f'retry_count {retry_count}')

            try:
                data = FilePayload.model_validate_json(body)
                logger.info(data)
                status = data.scan_status
                ttl = generate_ttl(retry_count)
                if status:
                    logger.info(f"Alert message sending with {data.processing_status}")
                    async for session in get_async_session():
                        await send_alert(session, data)
                    await message.ack()
                else:
                    if retry_count < max_retries:
                        logger.error("Failed to send alert -> to retry queue")
                        await publish_status_retry(body, retry_count + 1, ttl)
                    else:
                        logger.error("Failed to send alert max_retries exceeded -> to dlx queue")
                        async for session in get_async_session():
                            await send_alert(session, data)
                        await asyncio.gather(
                            publish_status_failed(body, retry_count, "Failed to send alert max_retries exceeded"),
                            message.ack()
                        )

            except pydantic_core._pydantic_core.ValidationError as e:
                logger.error(f"pydantic ValidationError while send alert with message {body}, {e}")
                logger.error("sent to the dead queue")
                await asyncio.gather(
                    publish_status_failed(body, retry_count, "ValidationError"),
                    message.ack()
                )

            except SQLAlchemyError as e:
                logger.info(f"SQLAlchemyError {e}")
                if retry_count < max_retries:
                    await publish_status_retry(body, retry_count + 1, ttl)
                else:
                    logger.error("SQLAlchemyError while send alert, exceeded number of retry -> to dead queue")
                    await asyncio.gather(
                        publish_status_failed(body, retry_count, "SQLAlchemyError max_retries exceeded"),
                        message.ack()
                    )

            except Exception as e:
                logger.critical(f"Unexpected error while send alert {e}")
                await asyncio.gather(
                    publish_status_failed(body, retry_count, f"Unexpected error {e}"),
                    message.ack()
                )

            except BaseException as e:
                logger.critical(f"While change scan_status processing error - {e}")

    async with rabbit_connector as connection:
        channel = await connection.channel()
# dead letters
        failed_queue = await channel.declare_queue("alert_failed", durable=True)
# retry status
        retry_queue = await channel.declare_queue(
            "alert_retry",
            durable=True,
            arguments={
                "x-dead-letter-exchange": "",
                "x-dead-letter-routing-key": "alert_queue",
            },
        )
# alert queue
        status_queue = await channel.declare_queue(
            "alert_queue",
            durable=True,
        )
        await status_queue.consume(callback_with_retry)
        logger.info("Alert worker started")
        await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass