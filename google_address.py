import os
import requests
import json
from dotenv import load_dotenv

# 若要看內容（測試用，正式勿列印金鑰）
# print("GOOGLE_API_KEY:", os.getenv("GOOGLE_API_KEY"))
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"

def address_to_latlng(address: str, region: str = "tw"):
    if not API_KEY:
        raise RuntimeError("API key not found. Set environment variable GOOGLE_API_KEY.")
    params = {
        "address": address,
        "key": API_KEY,
        "language": "zh-TW",
        "region": region
    }
    try:
        resp = requests.get(GEOCODE_URL, params=params, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        return {"ok": False, "error": f"HTTP error: {e}"}

    data = resp.json()

    # 印出完整回傳以供除錯
    print("GEOCODE RESPONSE:", json.dumps(data, ensure_ascii=False, indent=2))

    status = data.get("status")
    if status != "OK":
        err_msg = data.get("error_message") or status
        return {"ok": False, "error": f"Geocoding failed: {err_msg}"}

    first = data.get("results", [])[0]
    loc = first.get("geometry", {}).get("location", {})
    lat = loc.get("lat")
    lng = loc.get("lng")
    return {"ok": True, "lat": lat, "lng": lng, "formatted_address": first.get("formatted_address")}

if __name__ == "__main__":
    addr = "台中市南屯區黎明東街260號"
    res = address_to_latlng(addr)
    if res["ok"]:
        print(f"地址: {addr}")
        print(f"解析結果: {res['formatted_address']}")
        print(f"lat: {res['lat']}, lng: {res['lng']}")
    else:
        print("找不到經緯度或發生錯誤:", res["error"])