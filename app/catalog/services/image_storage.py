import uuid
from pathlib import Path

from fastapi import UploadFile

from app.catalog.exceptions import ImageTooLargeError, InvalidImageTypeError

BASE_DIR = Path(__file__).resolve().parent.parent.parent
MEDIA_ROOT = BASE_DIR / "media" / "products"
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_SIZE = 2 * 1024 * 1024


class ImageStorage:
    async def save_product_image(self, file: UploadFile) -> str:
        if file.content_type not in ALLOWED_IMAGE_TYPES:
            raise InvalidImageTypeError

        content = await file.read()
        if len(content) > MAX_IMAGE_SIZE:
            raise ImageTooLargeError

        extension = Path(file.filename or "").suffix.lower() or ".jpg"
        file_name = f"{uuid.uuid4()}{extension}"
        file_path = MEDIA_ROOT / file_name
        file_path.write_bytes(content)

        return f"/media/products/{file_name}"

    def remove_product_image(self, url: str | None) -> None:
        if not url:
            return
        relative_path = url.lstrip("/")
        file_path = BASE_DIR / relative_path
        if file_path.exists():
            file_path.unlink()
