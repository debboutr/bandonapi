import timeit
from typing import Annotated

from fastapi import Depends, FastAPI, Path, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from geoalchemy2 import WKTElement
from geoalchemy2.shape import to_shape
from pyproj import CRS, Transformer
from shapely.geometry import Point, Polygon
from shapely.ops import transform
from sqlalchemy.orm import Session

from .database import SessionLocal, engine
from .models import Base, Green
from .schemas import Measurement

m2y = 1.093613  # meters to yards

Base.metadata.create_all(bind=engine)


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
    print(str(rec))  # this is the way to get the SQL!!!
    # print(f"{[r.category for r in rec]=}")
    return rec.first()


app = FastAPI()

# origins = [
#     "https://nflsuicidepool.vercel.app",
#     "http://bandonapi.debbout.info",
#     "http://localhost:8074",
#     "http://127.0.0.1:8074",
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/measure", response_model=Measurement)
def read_distances(
    track: str,
    green: int,
    lon: float = -124.38400938,
    lat: float = 43.18070706,
    db: Session = Depends(get_db),
):
    """
    you should always check for a green intersection here!!!
    if abs(green_returned - current_hole) == 1:
        update state!!
    * add timer to see how long calls to this view are taking
    * return measurements, current hole intersected
    * how to deal with current hole from here to client?
    * would it make sense to just do the calcs for ALL holes?
    [ ] make the green images...
    """
    if track == "nowhere":
        # this is where you'll look for a track and a green
        # and you can give back measurements to closest green < 6
        # if there is one...
        return Measurement(front=0, center=0, back=0)
    # lat, lon = 43.17594092,-124.38642774 # 13th green of trails
    # lat, lon = 43.17419835396825, -124.38951194528615 # 15 fairway
    lat, lon = 43.17637634579635, -124.37251592314665  # home
    # lat, lon = 43.1847296,-124.3923103 # 1st tee of trails
    # lat, lon = 43.181944,-124.393064 # 1st green of trails
    # rec = get_grn(db, grn_id=grn_id)
    t1 = timeit.default_timer()
    point = transform_to_UTM(lon, lat)
    print(f"{point.wkt=}")
    bound = get_bounds(db, point)
    if not bound:
        return Measurement(course="nowhere", hole=19, front=47, center=47, back=47)
    rec = db.query(Green).filter(Green.green_no == bound.green_no).first()
    polygon = to_shape(rec.geometry)
    # print(f"{[p for p in polys]=}")
    distances = Measurement(
        course=rec.course,
        hole=rec.green_no,
        front=int(point.distance(polygon) * m2y),
        center=int(point.distance(polygon.centroid) * m2y),
        back=int(point.hausdorff_distance(polygon) * m2y),
    )
    # distances = get_distances(geom, home_point)
    print(f"{distances=}")
    t2 = timeit.default_timer()
    print("time to run: ", t2 - t1)
    return distances


@app.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
):
    context = {"request": request, "greens": f"{request.url}"}
    return templates.TemplateResponse("index.html", context)
