from pathlib import Path
from uuid import uuid4


class LocalDocumentStorage:
    def __init__(self, base_dir: str = "uploads/cv") -> None:
        self.base_dir = Path(base_dir)

    def save_cv(self, user_id: int, filename: str, content: bytes) -> str:
        safe_name = Path(filename or "cv").name.replace(" ", "_")
        user_dir = self.base_dir / str(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)

        target = user_dir / f"{uuid4().hex}_{safe_name}"
        target.write_bytes(content)
        return target.as_posix()

    def save_support(self, user_id: int, item_id: int, filename: str, content: bytes) -> str:
        safe_name = Path(filename or "soporte").name.replace(" ", "_")
        item_dir = Path("uploads/soportes") / str(user_id) / str(item_id)
        item_dir.mkdir(parents=True, exist_ok=True)

        target = item_dir / f"{uuid4().hex}_{safe_name}"
        target.write_bytes(content)
        return target.as_posix()

    def delete_file(self, relative_path: str) -> None:
        target = Path(relative_path)
        if target.exists():
            target.unlink()
