from sqlalchemy import insert, select, func, literal
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.outbox import OutboxMessage
from src.models.stored_file import StoredFile


async def upload_file_insert(
        session: AsyncSession,
        file_id,
        title,
        file_name,
        stored_name,
        mime,
        size,
        rabbit_queue
):
    async with session.begin():
        file_insert_stmt = (
            insert(StoredFile)
            .values(
                id=file_id,
                title=title,
                original_name=file_name or stored_name,
                stored_name=stored_name,
                mime_type=mime,
                size=size,
                processing_status="uploaded",
            )
            .returning(
                StoredFile.id,
                StoredFile.created_at,
                StoredFile.processing_status,
            )
            .cte("new_file")
        )

        outbox_stmt = insert(OutboxMessage).from_select(
            [
                OutboxMessage.file_id,
                OutboxMessage.payload,
                OutboxMessage.queue,
                OutboxMessage.processed,
            ],
            select(
                file_insert_stmt.c.id,
                func.json_build_object(
                    "file_id", file_insert_stmt.c.id,
                    "original_name", file_name or stored_name,
                    "stored_name", stored_name,
                    "mime_type", mime,
                    "size", size,
                ),
                literal(rabbit_queue),
                literal(False),
            ).select_from(file_insert_stmt)
        )

        await session.execute(outbox_stmt)
    return await session.get(StoredFile, file_id)


async def list_file_query(session, limit, offset):
    list_files_stmt = (
        select(StoredFile)
        .order_by(StoredFile.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return await session.execute(list_files_stmt)


async def get_file_query(session, file_id):
    return await session.get(StoredFile, file_id)


async def delete_file_query(session, file_item):
    await session.delete(file_item)
    await session.commit()


async def update_file_query(session, file_id, title):
    file_item = await session.get(StoredFile, file_id)
    if not file_item:
        return None
    file_item.title = title
    await session.commit()
    await session.refresh(file_item)
    return file_item