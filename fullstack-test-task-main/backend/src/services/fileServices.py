import mimetypes
from pathlib import Path
from typing import Type
from uuid import uuid4
import logging
import aiofiles
from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import FileResponse
from src.infrastructure.config import settings
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
    stored_path = settings.storage_dir / stored_name
    mime = (
        upload_file.content_type
        or mimetypes.guess_type(stored_name)[0]
        or "application/octet-stream"
    )

    max_size = settings.max_file_size
    size = 0
    chunks = []
    logger.debug('create_file start uploading file')

    while True:
        chunk = await upload_file.read(1024 * 1024)  # 1MiB
        if not chunk:
            break
        size += len(chunk)
        if size > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File is too large",
            )
        chunks.append(chunk)

    content = b"".join(chunks)
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="File is empty"
        )
    logger.debug('create_file file uploaded')

    await _save_uploaded_file(content, stored_path)

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
    stored_path = settings.storage_dir / file_item.stored_name
    if stored_path.exists():
        try:
            await aiofiles.os.remove(stored_path)
        except Exception:
            pass

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
) -> FileResponse:
    logger.debug('download_file_service start')
    file_item = await get_file_query(session, file_id)
    stored_path = settings.storage_dir / file_item.stored_name

    if not stored_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Stored file not found"
        )
    logger.debug('download_file_service end')
    logging.info(f'>download_file_service> File ID {file_id} Download Started')
    return FileResponse(
        path=stored_path,
        media_type=file_item.mime_type,
        filename=file_item.original_name,
    )
