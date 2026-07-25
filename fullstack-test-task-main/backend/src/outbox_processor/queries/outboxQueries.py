from sqlalchemy import update

from src.models.alert import Alert
from src.models.outbox import OutboxMessage
from src.models.stored_file import StoredFile


async def change_status(session, data) -> None:
    update_data = data.model_dump(exclude_unset=True, exclude={'file_id'})
    stmt = update(StoredFile).where(StoredFile.id == data.file_id).values(**update_data)
    await session.execute(stmt)
    await session.commit()


async def mark_outbox_message(session, data) -> None:
    stmt = update(OutboxMessage).where(OutboxMessage.file_id == data.file_id).values(processed=True)
    await session.execute(stmt)
    await session.commit()


async def send_alert(session, data) -> None:
    if data.processing_status == "failed":
        level = "critical"
        message = "File processing failed"

    elif data.requires_attention:
        level = "warning"
        message = (
            f"File requires attention: "
            f"{data.scan_details}"
        )
    else:
        level = "info"
        message = ("File processed successfully")

    alert = Alert(
        file_id=data.file_id,
        level=level,
        message=message
    )
    session.add(alert)
    await session.commit()