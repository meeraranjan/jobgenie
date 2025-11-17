from typing import Dict, Iterable, List, Tuple
import requests
from django.conf import settings

def geocode_address(address):
    if not address:
        return None, None

    api_key = settings.GOOGLE_MAPS_API_KEY
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": api_key}

    try:
        response = requests.get(url, params=params, timeout=5).json()
        if response.get("results"):
            loc = response["results"][0]["geometry"]["location"]
            return loc["lat"], loc["lng"]
    except Exception:
        pass

    return None, None

def distance_matrix_km(origin, destinations):
    if not origin or not destinations:
        return {}

    api_key = settings.GOOGLE_MAPS_API_KEY
    base_url = "https://maps.googleapis.com/maps/api/distancematrix/json"

    origin_str = f"{origin[0]},{origin[1]}"
    dest_str = "|".join(f"{lat},{lng}" for _, lat, lng in destinations)

    params = {
        "origins": origin_str,
        "destinations": dest_str,
        "key": api_key,
        "mode": "driving",
        "units": "metric",
    }

    try:
        resp = requests.get(base_url, params=params, timeout=5)
        data = resp.json()
    except Exception as e:
        print("Distance Matrix request error:", e)
        return None

    print("DM status:", data.get("status"))
    if data.get("status") != "OK":
        print("DM error_message:", data.get("error_message"))
        return None

    rows = data.get("rows", [])
    if not rows:
        return {}

    elements = rows[0].get("elements", [])
    results = {}
    for (job_id, _, _), el in zip(destinations, elements):
        if el.get("status") == "OK":
            meters = el["distance"]["value"]
            results[job_id] = meters / 1000.0
        else:
            results[job_id] = None

    return results