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
    """
    origin: (lat, lng)
    destinations: list of (job_id, lat, lng)
    returns dict: { job_id: distance_km }  -- only for jobs with a valid distance
    """
    if not origin or not destinations:
        print("DM: missing origin or destinations", origin, destinations)
        return {}

    api_key = settings.GOOGLE_MAPS_API_KEY
    url = "https://routes.googleapis.com/distanceMatrix/v2:computeRouteMatrix"

    origin_lat, origin_lng = origin

    body = {
        "origins": [
            {"location": {"latLng": {"latitude": origin_lat, "longitude": origin_lng}}}
        ],
        "destinations": [
            {"location": {"latLng": {"latitude": lat, "longitude": lng}}}
            for _, lat, lng in destinations
        ],
        "travelMode": "DRIVE",
        "units": "METRIC",
    }

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "originIndex,destinationIndex,distanceMeters,status",
    }

    try:
        resp = requests.post(url, json=body, headers=headers, timeout=8)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print("Routes API HTTP error:", e)
        try:
            print("Response text:", resp.text[:500])
        except Exception:
            pass
        return {}

    if isinstance(data, dict) and "error" in data:
        print("Routes API logical error:", data["error"])
        return {}

    if not isinstance(data, list):
        print("Routes API unexpected payload:", data)
        return {}

    results: Dict[int, float] = {}
    for (job_id, _, _), element in zip(destinations, data):
        status = element.get("status")
        if status == "OK" and "distanceMeters" in element:
            meters = element["distanceMeters"]
            results[job_id] = meters / 1000.0
        else:
            print("DM element not OK:", status, element)

    print("DM results (km):", results)
    return results