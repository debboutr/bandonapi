import pyproj
from pyproj import Geod
from shapely.geometry import Polygon, Point
from shapely.ops import transform

from .schemas import Measurement

m2y = 1.09361000 # meters to yards
# m2y = 0.9144 # meters to yards

def transform_to_UTM(lon: float, lat: float) -> Point:
    wgs84 = pyproj.CRS("EPSG:4326")
    utm = pyproj.CRS("EPSG:26910")
    project = pyproj.Transformer.from_crs(wgs84, utm, always_xy=True).transform
    pt = Point(lon, lat)
    return transform(project, pt)

def get_distances(polygon: Polygon, point: Point) -> Measurement:
    front = point.distance(polygon) * m2y
    center = point.distance(polygon.centroid) * m2y
    back = point.hausdorff_distance(polygon) * m2y
    return Measurement(
            front=int(front),
            center=int(center),
            back=int(back)
    )
