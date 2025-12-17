from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, UploadFile, File, HTTPException, status

router = APIRouter(prefix="/uploads", tags=["uploads"])


UPLOAD_DIR = Path("static") / "test-request-images"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/test-request-images")
async def upload_test_request_image(file: UploadFile = File(...)):
    """Upload an image for test request references and return its public URL."""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se permiten archivos de imagen.",
        )

    suffix = Path(file.filename or "").suffix or ".png"
    filename = f"{uuid4().hex}{suffix}"
    dest_path = UPLOAD_DIR / filename

    content = await file.read()
    dest_path.write_bytes(content)

    # URL served by FastAPI static files
    url = f"/static/test-request-images/{filename}"

    return {"url": url}


