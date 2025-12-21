from geoalchemy2.shape import to_shape
from geoalchemy2 import WKTElement
from sqlalchemy import func
from sqlalchemy.orm import Session
from shapely.geometry import Polygon, Point

from .models import Green

def get_intersecting_polys(db: Session, point: Point):
    rec = db.query(Green).filter(
            # both lines below work!!
            # func.ST_Contains(Green.geometry, WKTElement(point.wkt))
            Green.geometry.ST_Intersects(WKTElement(point.wkt))
            )
    print(str(rec)) # this is the way to get the SQL!!!
    print(f"{point.wkt=}")
    print(f"{[r.category for r in rec]=}")
    return rec

def get_grn(db: Session, grn_id: int):
    rec = db.query(Green).filter(Green.green_no == grn_id).first()
    return rec
