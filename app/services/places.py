import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Coordinates:
    lat: float
    lon: float


_PLACES_PATH = Path(__file__).resolve().parents[2] / "data" / "places.json"


def load_places() -> dict[str, dict[str, float]]:
    with _PLACES_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def find_coordinates(place: str) -> Coordinates:
    places = load_places()
    key = place.strip()

    if key not in places:
        raise ValueError(f"Unknown place: {key}")

    item = places[key]
    return Coordinates(lat=float(item["lat"]), lon=float(item["lon"]))