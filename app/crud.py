from geoalchemy2.shape import to_shape
from sqlalchemy.orm import Session

from . import models, schemas


def get_grn(db: Session, grn_id: int):
    rec = db.query(models.Green).filter(models.Green.green_no == grn_id).first()
    return rec
