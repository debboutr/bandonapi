from pydantic import BaseModel


class Measurement(BaseModel):
    front: int
    center: int
    back: int
