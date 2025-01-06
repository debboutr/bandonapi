from sqlalchemy import Column, Integer, String

# from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry

from .database import Base


class Green(Base):
    __tablename__ = "greens"
    ogc_fid = Column(Integer, primary_key=True, index=True)
    green_no = Column(Integer)
    category = Column(String(10))
    course = Column(String(10))
    geometry = Column(Geometry("POLYGON"))
