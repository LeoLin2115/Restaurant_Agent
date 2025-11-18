# improved_overpass.py
import requests
import csv
import time
from requests.exceptions import RequestException
import json

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

def geocode_address_nominatim(address, retries=2):
    url = "https://nominatim.openstreetmap.org/search"
    headers = {"User-Agent": "my-osm-app/1.0 (fish32206@gmail.com)"}
    params = {"q": address, "format": "json", "limit": 1}
    for attempt in range(retries+1):
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=10)
        except RequestException as e:
            if attempt < retries:
                time.sleep(1)
                continue
            raise RuntimeError(f"Nominatim 請求失敗: {e}")
        if resp.status_code != 200:
            raise RuntimeError(f"Nominatim 非 200 回應: {resp.status_code} 內容: {resp.text[:300]}")
        try:
            data = resp.json()
        except json.JSONDecodeError:
            raise RuntimeError(f"Nominatim 回傳非 JSON 內容: {resp.text[:300]}")
        if not data:
            raise ValueError("Nominatim 無搜尋結果，請確認地址是否完整或改用經緯度")
        return float(data[0]["lat"]), float(data[0]["lon"])
    raise RuntimeError("無法取得地理編碼")

def build_overpass_query(lat, lon, radius_m):
    q = f"""
    [out:json][timeout:25];
    (
      node["amenity"="restaurant"](around:{radius_m},{lat},{lon});
      way["amenity"="restaurant"](around:{radius_m},{lat},{lon});
      relation["amenity"="restaurant"](around:{radius_m},{lat},{lon});
    );
    out center tags;
    """
    return q

def query_overpass(lat, lon, radius_m):
    headers = {"User-Agent": "my-osm-app/1.0 (fish32206@gmail.com)"}
    q = build_overpass_query(lat, lon, radius_m)
    try:
        resp = requests.post(OVERPASS_URL, data={'data': q}, headers=headers, timeout=60)
    except RequestException as e:
        raise RuntimeError(f"Overpass 請求失敗: {e}")
    if resp.status_code != 200:
        raise RuntimeError(f"Overpass 非 200 回應: {resp.status_code} 內容: {resp.text[:500]}")
    try:
        data = resp.json()
    except json.JSONDecodeError:
        raise RuntimeError(f"Overpass 回傳非 JSON 內容: {resp.text[:500]}")
    return data.get("elements", [])

def parse_elements(elements):
    parsed = []
    for el in elements:
        tags = el.get("tags", {})
        name = tags.get("name") or ""
        if el.get("type") == "node":
            lat = el.get("lat")
            lon = el.get("lon")
        else:
            center = el.get("center") or {}
            lat = center.get("lat")
            lon = center.get("lon")
        parsed.append({
            "name": name,
            "osm_type": el.get("type"),
            "osm_id": el.get("id"),
            "address": tags.get("addr:full") or tags.get("addr:street") or "",
            "lat": lat,
            "lng": lon,
            "cuisine": tags.get("cuisine") or "",
            "price": tags.get("price") or tags.get("price_range") or "",
        })
    return parsed

def save_to_csv(rows, filename="restaurants_osm.csv"):
    keys = ["name","address","lat","lng","cuisine","price","osm_type","osm_id"]
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

def build_restaurant_list(lat = 24.1480614, lng = 120.6369732, radius = 500):
    address = str(lat) + "," + str(lng)
    # address = input("請輸入地址 (或輸入 lat,lng): ").strip()
    # radius = input("請輸入距離（公尺）: ").strip()
    try:
        radius_m = int(radius)
    except:
        print("距離請輸入整數（公尺）")
        return
    # 若使用者直接輸入經緯度 "lat,lon"
    if "," in address:
        try:
            lat, lon = map(float, address.split(","))
        except:
            print("經緯度格式錯誤，請用 'lat,lon'（例如 24.14,120.647）或改用中文地址")
            return
    else:
        print("解析地址中...")
        try:
            lat, lon = geocode_address_nominatim(address)
        except Exception as e:
            print("發生錯誤：", e)
            return
    try:
        elements = query_overpass(lat, lon, radius_m)
        parsed = parse_elements(elements)
    except Exception as e:
        print("發生錯誤：", e)
        return
    
    if not parsed:
        print("查無餐廳")
    else:
        save_to_csv(parsed, "restaurants_osm.csv")
        print(f"已寫入 {len(parsed)} 筆到 restaurants_osm.csv")

if __name__ == "__main__":
    # address = input("請輸入地址: ").strip()
    # radius = input("請輸入距離（公尺）: ").strip()
    build_restaurant_list()