from pydantic import BaseModel


class Config(BaseModel):
    filehost_url_base: str
    filehost_url_prefix: str = "/i"
