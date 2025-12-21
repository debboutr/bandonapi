from typing import Annotated
from fastapi import Depends, FastAPI, Request, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from geoalchemy2.shape import to_shape
from sqlalchemy.orm import Session

from .crud import get_intersecting_polys, get_grn 
from .models import Base, Green
from .schemas import Measurement
from .database import SessionLocal, engine
from .utils import get_distances, transform_to_UTM

Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "https://nflsuicidepool.vercel.app",
    "http://bandonapi.debbout.info",
    "http://localhost",
    "http://localhost:8074",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/{course}/{grn_id}", response_model=Measurement)
def read_distances(
    course: str,
    grn_id: int,
    lon: float = -124.38400938,
    lat: float = 43.18070706,
    db: Session = Depends(get_db),
):
    """
    you should always check for a green intersection here!!!
    if abs(green_returned - current_hole) == 1:
        update state!!
    """
    if course == "nowhere":
        # this is where you'll look for a course and a green
        # and you can give back measurements to closest green < 6
        # if there is one...
        return Measurement(front=0, center=0, back=0)
    # lat, lon = 43.17594092,-124.38642774
    # lat, lon = 43.1847296,-124.3923103 # first tee of trails
    # lat, lon = 43.184750507,-124.392289776
    lat, lon = 43.181944,-124.393064
    # rec = get_grn(db, grn_id=grn_id)
    rec = db.query(Green).filter(Green.green_no == grn_id).first()
    geom = to_shape(rec.geometry)
    home_point = transform_to_UTM(lon, lat)
    print(f"{home_point.wkt=}")
    polys = get_intersecting_polys(db, home_point)
    print(f"{[p for p in polys]=}")
    distances = get_distances(geom, home_point)
    print(f"{distances=}")
    return distances

@app.get("/", response_class=HTMLResponse)
async def index( request: Request,):
    context = { "request": request, "greens": range(1, 19) }
    return templates.TemplateResponse("index.html", context)
