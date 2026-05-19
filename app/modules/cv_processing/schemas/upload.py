from pydantic import BaseModel


class UploadPreparedResponse(BaseModel):
    filename: str
    content_type: str | None = None
    message: str
