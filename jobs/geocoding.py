from __future__ import annotations
from typing import Optional, Tuple, Dict, Any
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

_geolocator = Nominatim(user_agent="cs2340-jobfinder-gt-talantbekova2")
_geocode = RateLimiter(_geolocator.geocode, min_delay_seconds=1)
_reverse = RateLimiter(_geolocator.reverse, min_delay_seconds=1)

STATE_ABBREVIATIONS = {
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR",
    "california": "CA", "colorado": "CO", "connecticut": "CT", "delaware": "DE",
    "florida": "FL", "georgia": "GA", "hawaii": "HI", "idaho": "ID",
    "illinois": "IL", "indiana": "IN", "iowa": "IA", "kansas": "KS",
    "kentucky": "KY", "louisiana": "LA", "maine": "ME", "maryland": "MD",
    "massachusetts": "MA", "michigan": "MI", "minnesota": "MN", "mississippi": "MS",
    "missouri": "MO", "montana": "MT", "nebraska": "NE", "nevada": "NV",
    "new hampshire": "NH", "new jersey": "NJ", "new mexico": "NM", "new york": "NY",
    "north carolina": "NC", "north dakota": "ND", "ohio": "OH", "oklahoma": "OK",
    "oregon": "OR", "pennsylvania": "PA", "rhode island": "RI", "south carolina": "SC",
    "south dakota": "SD", "tennessee": "TN", "texas": "TX", "utah": "UT",
    "vermont": "VT", "virginia": "VA", "washington": "WA", "west virginia": "WV",
    "wisconsin": "WI", "wyoming": "WY", "district of columbia": "DC"
}

def _normalize_state(state_value: str) -> str:
    if not state_value:
        return ""

    state_value = state_value.strip()
    if len(state_value) == 2:
        return state_value.upper()

    return STATE_ABBREVIATIONS.get(state_value.lower(), state_value[:2].upper())

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

def reverse_geocode_us(latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
    try:
        loc = _reverse((latitude, longitude), exactly_one=True, language="en")
    except Exception:
        return None

    if not loc:
        return None

    raw = loc.raw.get("address", {})

    house_number = raw.get("house_number", "").strip()
    road = (
        raw.get("road")
        or raw.get("pedestrian")
        or raw.get("footway")
        or raw.get("residential")
        or ""
    ).strip()

    street_address = " ".join(part for part in [house_number, road] if part).strip()

    city = (
        raw.get("city")
        or raw.get("town")
        or raw.get("village")
        or raw.get("hamlet")
        or raw.get("municipality")
        or ""
    ).strip()

    state = _normalize_state(
        raw.get("state_code")
        or raw.get("state")
        or ""
    )

    zip_code = (raw.get("postcode") or "").strip()
    if len(zip_code) > 10:
        zip_code = zip_code[:10]

    return {
        "display_name": loc.address,
        "street_address": street_address,
        "city": city,
        "state": state,
        "zip_code": zip_code,
        "latitude": float(latitude),
        "longitude": float(longitude),
    }