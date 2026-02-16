from __future__ import annotations
from typing import Optional, Tuple
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

_geolocator = Nominatim(user_agent="cs2340-jobfinder-gt-talantbekova2")
_geocode = RateLimiter(_geolocator.geocode, min_delay_seconds=1)

def geocode_us(location_text: str) -> Optional[Tuple[float, float]]:
    if not location_text:
        return None

    query = location_text.strip()
    if not query:
        return None

    q_lower = query.lower()
    if "usa" not in q_lower and "united states" not in q_lower:
        query = f"{query}, USA"

    try:
        loc = _geocode(query, country_codes="us")
    except Exception:
        return None

    if not loc:
        return None

    return float(loc.latitude), float(loc.longitude)
