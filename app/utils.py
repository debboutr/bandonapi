import pyproj
from pyproj import Geod
from shapely.geometry import Point
from shapely.ops import transform


def transform_to_UTM(lon: float, lat: float) -> Point:
    wgs84 = pyproj.CRS("EPSG:4326")
    utm = pyproj.CRS("EPSG:26910")
    project = pyproj.Transformer.from_crs(wgs84, utm, always_xy=True).transform
    pt = Point(lon, lat)
    return transform(project, pt)


def inverse_transformation(
    start_lon: float, start_lat: float, end_lon: float, end_lat: float
):
    geod = Geod(ellps="WGS84")
    return geod.inv(start_lon, start_lat, end_lon, end_lat)
