from pydantic import BaseModel


class Measurement(BaseModel):
    course: str
    hole: int
    front: int
    center: int
    back: int
