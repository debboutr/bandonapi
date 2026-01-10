import os
import timeit
from typing import Annotated

from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from geoalchemy2 import WKTElement
from geoalchemy2.shape import to_shape
from pydantic import BaseModel
from pyproj import CRS, Transformer
from shapely.geometry import Point
from shapely.ops import transform
from sqlalchemy.orm import Session

from .database import SessionLocal, engine
from .models import Base, Green


class Response(BaseModel):
    course: str = "None"
    hole: int = 19
    front: int = 0
    center: int = 0
    back: int = 0


def transform_to_UTM(lon: float, lat: float) -> Point:
    wgs84 = CRS("EPSG:4326")
    utm = CRS("EPSG:26910")
    project = Transformer.from_crs(wgs84, utm, always_xy=True).transform
    pt = Point(lon, lat)
    return transform(project, pt)


def get_bounds(db: Session, point: Point):
    rec = (
        db.query(Green)
        .filter(Green.category == "bounds")
        .filter(  # both lines below work!!
            # func.ST_Contains(Green.geometry, WKTElement(point.wkt))
            Green.geometry.ST_Intersects(WKTElement(point.wkt))
        )
    )
    # print(str(rec))  # this is the way to get the SQL!!!
    return rec.first()


m2y = 1.093613  # meters to yards

Base.metadata.create_all(bind=engine)

app = FastAPI()

templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/measure", response_model=Response)
def read_distances(
    track: str,
    green: int,
    lon: float = -124.38400938,
    lat: float = 43.18070706,
    db: Session = Depends(get_db),
):
    """
    * how to deal with current hole from here to client?
    * would it make sense to just do the calcs for ALL holes?
    [ ] make the green images...
    """
    if track == "nowhere":
        return Response(front=0, center=0, back=0)
    # lat, lon = 43.17594092,-124.38642774 # 13th green of trails
    # lat, lon = 43.17419835396825, -124.38951194528615 # 15 fairway
    # lat, lon = 43.17637634579635, -124.37251592314665  # home
    lat, lon = 43.18647178212453, -124.39929791179547  # 16 bandon fairway
    # lat, lon = 43.1847296,-124.3923103 # 1st tee of trails
    # lat, lon = 43.181944,-124.393064 # 1st green of trails
    t1 = timeit.default_timer()
    point = transform_to_UTM(lon, lat)
    # print(f"{point.wkt=}")
    bound = get_bounds(db, point)
    if not bound:
        return Response()
    rec = (
        db.query(Green)
        .filter(Green.course == bound.course)
        .filter(Green.green_no == bound.green_no)
        .first()
    )
    polygon = to_shape(rec.geometry)
    t2 = timeit.default_timer()
    print("time to run: ", t2 - t1)
    return Response(
        course=rec.course,
        hole=rec.green_no,
        front=int(point.distance(polygon) * m2y),
        center=int(point.distance(polygon.centroid) * m2y),
        back=int(point.hausdorff_distance(polygon) * m2y),
    )


@app.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
):
    context = {"request": request, "base_url": f"{os.getenv('BANDON_API')}"}
    return templates.TemplateResponse("index.html", context)
