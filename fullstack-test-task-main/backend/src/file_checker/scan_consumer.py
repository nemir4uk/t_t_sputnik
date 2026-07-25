import asyncio
import logging
import aio_pika
from aio_pika import Message, DeliveryMode
import pydantic_core
from src.file_checker.file_check_utils import scan_file_for_threats
from src.infrastructure.broker.rabbitmq import rabbit_connector
from src.schemas.messagesSchemas import FilePayload, ScanStatus
from src.infrastructure.config import settings

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=settings.log_level.upper(),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


async def main():
    async def publish_failed(body: bytes, retry_count: int, error: str):
        await channel.default_exchange.publish(
            Message(
                body=body,
                headers={
                    "x-retry-count": retry_count,
                    "x-error": error,
                },
                delivery_mode=DeliveryMode.PERSISTENT,
            ),
            routing_key="failed",
        )

    async def publish_retry(body: bytes, retry_count: int, delay: int):
        await channel.default_exchange.publish(
            Message(
                body=body,
                headers={
                    "x-retry-count": retry_count,
                },
                expiration=delay,
                delivery_mode=DeliveryMode.PERSISTENT,
            ),
            routing_key="retry",
        )

    async def publish_status(body: bytes):
        await channel.default_exchange.publish(
            Message(
                body=body,
                delivery_mode=DeliveryMode.PERSISTENT,
            ),
            routing_key="scan_status_queue",
        )

    async def publish_to_check_metadata(body: bytes):
        await channel.default_exchange.publish(
            Message(
                body=body,
                delivery_mode=DeliveryMode.PERSISTENT,
            ),
            routing_key="check_metadata_queue",
        )

    async def callback_with_retry(message: aio_pika.IncomingMessage):
        async with message.process(ignore_processed=True):
            logger.info("Scan_consumer message received")

            headers = message.headers or {}
            retry_count = headers.get("x-retry-count", 0)

            max_retries = settings.retry_count
            body = message.body
            logger.info(f'retry_count {retry_count}')

            try:
                data = FilePayload.model_validate_json(body)
                file_item, ttl = await asyncio.to_thread(scan_file_for_threats, data, retry_count)
                if file_item.processing_status == "processing":
                    logger.info("Scan_consumer Success process scan_file_for_threats")
                    data.scan_status = ScanStatus.success_check
                    await asyncio.gather(
                        publish_status(data.model_dump_json().encode()),
                        message.ack(),
                        publish_to_check_metadata(data.model_dump_json().encode())
                    )
                else:
                    if retry_count < max_retries:
                        logger.error("Scan_consumer Failed process scan_file_for_threats -> to retry queue")
                        await publish_retry(data.model_dump_json().encode(), retry_count + 1, ttl)
                    else:
                        logger.error("Scan_consumer Failed process scan_file_for_threats max_retries exceeded -> to dlx queue")
                        data.scan_status = ScanStatus.failed_check
                        await asyncio.gather(
                            publish_status(data.model_dump_json().encode()),
                            publish_failed(data.model_dump_json().encode(), retry_count,
                                           "Scan_consumer process scan_file_for_threats max_retries exceeded"),
                            message.ack()
                        )

            except pydantic_core._pydantic_core.ValidationError as e:
                logger.error(f"pydantic ValidationError with message {body}, {e}")
                logger.error("sent to the dead queue")
                data.scan_status = ScanStatus.failed_check
                await asyncio.gather(
                    publish_status(data.model_dump_json().encode()),
                    publish_failed(data.model_dump_json().encode(), retry_count, "ValidationError"),
                    message.ack()
                )

            except Exception as e:
                logger.critical(f"Unexpected error {e}")
                data.scan_status = ScanStatus.failed_check
                await asyncio.gather(
                    publish_status(data.model_dump_json().encode()),
                    publish_failed(data.model_dump_json().encode(), retry_count, f"Unexpected error {e}"),
                    message.ack()
                )

            except BaseException as e:
                logger.critical(f"Processing error - {e}")

    async with rabbit_connector as connection:
        channel = await connection.channel()
# dead letters
        failed_queue = await channel.declare_queue("failed", durable=True)
# retry
        retry_queue = await channel.declare_queue(
            "retry",
            durable=True,
            arguments={
                "x-dead-letter-exchange": "",
                "x-dead-letter-routing-key": settings.rabbit_queue,
            },
        )
# main
        main_queue = await channel.declare_queue(
            settings.rabbit_queue,
            durable=True,
        )
        await main_queue.consume(callback_with_retry)
        logger.info("Scan_consumer started")
        await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
