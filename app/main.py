from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from geoalchemy2.shape import to_shape
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine
from . import utils

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "https://nflsuicidepool.vercel.app",
    "http://bandonapi.debbout.info",
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

m2y = 1.09361000


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/green/{grn_id}", response_model=schemas.Measurement)
def read_distances(
    grn_id: int,
    lon: float = -124.38400938,
    lat: float = 43.18070706,
    db: Session = Depends(get_db),
):
    rec = crud.get_grn(db, grn_id=grn_id)
    _, _, dist = utils.inverse_transformation(lon, lat, rec.lon, rec.lat)
    home_point = utils.transform_to_UTM(lon, lat)
    geom = to_shape(rec.geom)
    front = home_point.distance(geom) * m2y
    back = home_point.hausdorff_distance(geom) * m2y
    center = dist * m2y
    return dict(
        front=front,
        center=center,
        back=back,
    )
