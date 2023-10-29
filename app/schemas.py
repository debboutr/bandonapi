from pydantic import BaseModel


class Measurement(BaseModel):
    front: float
    center: float
    back: float
