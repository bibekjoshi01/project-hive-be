import pathlib
import secrets
import shutil
from fastapi import HTTPException, UploadFile, status, Request
from typing import Optional

MEDIA_ROOT = pathlib.Path("media")


def save_upload_file(
    file: UploadFile,
    subdir: Optional[str] = "other",
    allowed_extensions: Optional[set[str]] = None,
) -> str:
    """
    Save an uploaded file to MEDIA_ROOT / subdir and return the relative URL path.

    Args:
        file (UploadFile): The uploaded file object from FastAPI.
        subdir (str, optional): Subdirectory inside MEDIA_ROOT to save the file. Defaults to 'user/photos'.
        allowed_extensions (set[str], optional): Allowed file extensions including dot, e.g. {'.png', '.jpg'}.
            If None, all extensions are allowed.

    Returns:
        str: Relative URL path to the saved file (e.g. '/media/user/photos/filename.png').

    Raises:
        400Exception: If the file extension is not allowed.
    """
    # Normalize subdir and prevent directory traversal
    safe_subdir = (
        pathlib.Path(subdir).resolve().relative_to(pathlib.Path.cwd().resolve())
    )
    target_dir = MEDIA_ROOT / safe_subdir
    target_dir.mkdir(parents=True, exist_ok=True)

    ext = pathlib.Path(file.filename).suffix.lower()

    if allowed_extensions and ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Extension '{ext}' not allowed. Allowed: {allowed_extensions}",
        )

    # Generate a unique filename
    filename = f"{secrets.token_hex(16)}{ext}"
    file_path = target_dir / filename

    # Reset file pointer before reading
    file.file.seek(0)
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file.file.close()

    return f"/media/{safe_subdir}/{filename}"


def get_full_url(request: Request, relative_url: str) -> str:
    # Remove leading slash if any
    relative_url = relative_url.lstrip("/")
    return str(request.base_url) + relative_url