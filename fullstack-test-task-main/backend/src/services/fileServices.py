import asyncio
import mimetypes
from pathlib import Path
from typing import Type
from uuid import uuid4
import logging
import aiofiles
from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import StreamingResponse
from src.infrastructure.config import settings
from src.infrastructure.file_storage.minio import minio_client
from src.models.stored_file import StoredFile
from src.services.queries.fileQueries import upload_file_insert, list_file_query, get_file_query, update_file_query, \
    delete_file_query

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=settings.log_level.upper(),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


async def _save_uploaded_file(content: bytes, filename: str) -> Path:
    logger.debug('_save_uploaded_file start')
    async with aiofiles.open(filename, "wb") as f:
        await f.write(content)
    logger.debug('_save_uploaded_file end')
    return Path(filename)


async def list_files(
        session: AsyncSession,
        limit: int = 100,
        offset: int = 0
) -> list[StoredFile]:
    logger.debug('list_files start')
    result = await list_file_query(session, limit, offset)
    logger.debug('list_files end')
    return list(result.scalars().all())


async def get_file(
        session: AsyncSession,
        file_id: str
) -> Type[StoredFile]:
    logger.debug('get_file start')
    file_item = await get_file_query(session, file_id)
    if not file_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )
    logger.debug('get_file end')
    return file_item


async def create_file(
        session: AsyncSession,
        title: str,
        upload_file: UploadFile
) -> StoredFile:
    logger.debug('create_file start')
    if upload_file.file is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No file provided"
        )

    file_id = uuid4()
    file_name = upload_file.filename
    suffix = Path(file_name or "").suffix
    stored_name = f"{file_id}{suffix}"

    mime = (
        upload_file.content_type
        or mimetypes.guess_type(stored_name)[0]
        or "application/octet-stream"
    )

    logger.debug('create_file start uploading file')

    size = upload_file.size

    if size is not None and size > settings.max_file_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File is too large"
        )
    logger.debug('create_file file uploaded')

    await asyncio.to_thread(
        minio_client.put_object,
        bucket_name=settings.s3_bucket,
        object_name=stored_name,
        data=upload_file.file,
        length=-1,
        part_size=10 * 1024 * 1024,
        content_type=mime,
    )

    file_item = await upload_file_insert(
        session, file_id, title, file_name, stored_name, mime, size, settings.rabbit_queue
    )

    logging.info(f'>create_file> New File Uploaded {file_name}')
    logger.debug('create_file end')
    return file_item


async def update_file(
        session: AsyncSession,
        file_id: str,
        title: str
) -> Type[StoredFile]:
    logger.debug('update_file start')
    file_item = await update_file_query(session, file_id, title)
    if not file_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )
    logging.info(f'>update_file> File ID {file_id} Updated')
    logger.debug('update_file end')
    return file_item


async def delete_file(
        session: AsyncSession,
        file_id: str
) -> None:
    logger.debug('delete_file start')
    file_item = await get_file_query(session, file_id)
    if not file_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )
    try:
        await asyncio.to_thread(
            minio_client.remove_object,
            settings.s3_bucket,
            file_item.stored_name,
        )
    except Exception as e:
        logger.warning(
            f"MinIO delete failed: {e}"
        )

    await delete_file_query(session, file_item)
    logging.info(f'>delete_file> File ID {file_id} Deleted')
    logger.debug('delete_file end')


async def get_file_path(
        session: AsyncSession,
        file_id: str
) -> tuple[StoredFile, Path]:
    logger.debug('get_file_path start')
    file_item = await get_file_query(session, file_id)
    stored_path = settings.storage_dir / file_item.stored_name
    if not stored_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Stored file not found"
        )
    logger.debug('get_file_path end')
    return file_item, stored_path


async def download_file_service(
        session: AsyncSession,
        file_id: str
) -> StreamingResponse:
    logger.debug('download_file_service start')
    file_item = await get_file_query(session, file_id)

    if not file_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Stored file not found"
        )

    try:
        response = await asyncio.to_thread(
            minio_client.get_object,
            settings.s3_bucket,
            file_item.stored_name,
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stored file not found"
        )
    logger.debug('download_file_service end')
    logging.info(f'>download_file_service> File ID {file_id} Download Started')
    return StreamingResponse(
        response,
        media_type=file_item.mime_type,
        headers={
            "Content-Disposition":
                f'attachment; filename="{file_item.original_name}"'
        }
    )
