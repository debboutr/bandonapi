from sqlalchemy import Column, Integer, Float

# from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry

from .database import Base


class Green(Base):
    __tablename__ = "greens"
    ogc_fid = Column(Integer, primary_key=True, index=True)
    fid = Column(Integer, primary_key=True, index=True)
    number = Column(Integer)
    lon = Column(Float)
    lat = Column(Float)
    geom = Column(Geometry("POLYGON"))
