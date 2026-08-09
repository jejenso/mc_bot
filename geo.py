import datetime
from zoneinfo import ZoneInfo

from timezonefinder import TimezoneFinder

_tf = TimezoneFinder()


def offset_from_coords(lat: float, lon: float) -> float | None:
    """Возвращает смещение от UTC в часах (например 6.0 или 5.5) или None, если не удалось определить."""
    try:
        tz_name = _tf.timezone_at(lat=lat, lng=lon)
        if not tz_name:
            return None
        tz = ZoneInfo(tz_name)
        now = datetime.datetime.now(tz)
        offset = now.utcoffset()
        if offset is None:
            return None
        return round(offset.total_seconds() / 3600, 2)
    except Exception:
        return None
