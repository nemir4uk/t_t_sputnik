from typing import List

from fastapi import Form, UploadFile, File, Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import StreamingResponse

from src.infrastructure.db.sessions import get_async_session
from src.schemas.filesSchemas import FileItem, FileUpdate
from src.services.fileServices import list_files, create_file, get_file, update_file, delete_file, download_file_service

files_router = APIRouter()


@files_router.get("/files", response_model=List[FileItem])
async def list_files_view(
        limit: int = 100,
        offset: int = 0,
        session: AsyncSession = Depends(get_async_session)
):
    return await list_files(limit=limit, offset=offset, session=session)


@files_router.post(
    "/files",
    response_model=FileItem,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a new file",
)
async def create_file_view(
        title: str = Form(...),
        file: UploadFile = File(...),
        session: AsyncSession = Depends(get_async_session)
):
    return await create_file(title=title, upload_file=file, session=session)


@files_router.get("/files/{file_id}", response_model=FileItem, summary="Get file meta")
async def get_file_view(
        file_id: str,
        session: AsyncSession = Depends(get_async_session)
):
    return await get_file(session, file_id)


@files_router.patch("/files/{file_id}", response_model=FileItem, summary="Rename file")
async def update_file_view(
        file_id: str,
        payload: FileUpdate,
        session: AsyncSession = Depends(get_async_session)
):
    return await update_file(file_id=file_id, title=payload.title, session=session)


@files_router.get(
    "/files/{file_id}/download",
    summary="Download raw file",
    response_description="Binary content of the stored file",
)
async def download_file(
        file_id: str,
        session: AsyncSession = Depends(get_async_session)
) -> StreamingResponse:
    return await download_file_service(session, file_id)


@files_router.delete(
    "/files/{file_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete file and its metadata",
)
async def delete_file_view(
        file_id: str,
        session: AsyncSession = Depends(get_async_session)
):
    await delete_file(session, file_id)
    return None