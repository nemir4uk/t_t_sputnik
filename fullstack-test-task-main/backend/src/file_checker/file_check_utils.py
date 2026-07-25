import logging
import math
from pathlib import Path
from src.infrastructure.config import settings
from src.infrastructure.file_storage.minio import minio_client

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=settings.log_level.upper(),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


def scan_file_for_threats(file_item, retry_count):
    logger.debug('Start scan_file_for_threats')
    file_item.processing_status = "processing"
    reasons = []
    extension = Path(
        file_item.original_name
    ).suffix.lower()

    if extension in {
        ".exe",
        ".bat",
        ".cmd",
        ".sh",
        ".js"
    }:
        reasons.append(
            f"suspicious extension {extension}"
        )

    if file_item.size > settings.max_file_size:
        reasons.append(
            f"file is larger than {settings.max_file_size / 1024 / 1024}MB"
        )

    if (
        extension == ".pdf"
        and file_item.mime_type not in {
            "application/pdf",
            "application/octet-stream",
        }
    ):
        reasons.append(
            "pdf extension does not match mime type"
        )

    file_item.scan_status = (
        "suspicious"
        if reasons
        else "clean"
    )
    file_item.scan_details = (
        ", ".join(reasons)
        if reasons
        else "no threats found"
    )
    file_item.requires_attention = bool(reasons)
    logger.debug('End scan_file_for_threats')
    ttl = math.exp(retry_count + 1)
    return file_item, ttl


def extract_file_metadata(file_item, retry_count):
    logger.debug('Start extract_file_metadata')
    ttl = math.exp(retry_count + 1)
    response = None
    try:
        response = minio_client.get_object(
            settings.s3_bucket,
            file_item.stored_name,
        )
        raw = response.read()
        metadata = {
            "extension": Path(
                file_item.original_name
            ).suffix.lower(),
            "size_bytes": file_item.size,
            "mime_type": file_item.mime_type,
        }

        if file_item.mime_type.startswith("text/"):
            content = raw.decode(
                "utf-8",
                errors="ignore"
            )
            metadata["line_count"] = len(
                content.splitlines()
            )
            metadata["char_count"] = len(content)

        elif file_item.mime_type == "application/pdf":
            metadata["approx_page_count"] = max(
                raw.count(b"/Type /Page"),
                1
            )

        file_item.metadata_json = metadata
        file_item.processing_status = "processed"
        logger.debug('End extract_file_metadata with status PROCESSED')
        return file_item, ttl

    except Exception as e:
        logger.error(
            f"MinIO object read failed: {e}"
        )
        file_item.processing_status = "failed"
        file_item.scan_details = (
            "stored file not found "
            "during metadata extraction"
        )
        logger.debug('End extract_file_metadata with status FAILED')
        return file_item, ttl
    finally:
        if response is not None:
            try:
                response.close()
                response.release_conn()
            except Exception as e:
                logger.debug(f'extract_file_metadata exception {e}')
