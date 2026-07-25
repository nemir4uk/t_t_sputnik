from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from src.api.alerts import alerts_router
from src.api.files import files_router
from src.infrastructure.file_storage.minio import init_bucket


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_bucket()
    yield

app = FastAPI(title="File‑store API", version="0.1.0", lifespan=lifespan)

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://192.168.1.7:3000",
    "http://192.168.1.10:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router=alerts_router)
app.include_router(router=files_router)

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)