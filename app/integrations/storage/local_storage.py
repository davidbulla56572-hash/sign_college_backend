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
