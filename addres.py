import requests
import time
import sys

USER_AGENT = "my-geocoder-script/1.0 (contact: fish32206@gmail.com)"

def geocode_nominatim_debug(address, timeout=10, pause=1.0, max_retries=2):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json",
        "addressdetails": 0,
        "limit": 1,
        "accept-language": "zh-TW"
    }
    headers = {"User-Agent": USER_AGENT}
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=timeout)
            print(f"[DEBUG] HTTP {resp.status_code} (attempt {attempt})", file=sys.stderr)
            resp.raise_for_status()
            data = resp.json()
            print(f"[DEBUG] raw response: {data}", file=sys.stderr)
            if not data:
                # 可能為空結果（找不到）；不一定是錯誤
                return None
            item = data[0]
            lat = float(item["lat"])
            lon = float(item["lon"])
            time.sleep(pause)
            return lat, lon
        except requests.HTTPError as e:
            print(f"[ERROR] HTTP error: {e} - resp text: {resp.text[:400]}", file=sys.stderr)
        except requests.RequestException as e:
            print(f"[ERROR] Request failed: {e}", file=sys.stderr)
        except ValueError as e:
            print(f"[ERROR] JSON / parse error: {e}", file=sys.stderr)
        # 若還有重試次數，等待再重試
        if attempt < max_retries:
            time.sleep(1.0)
    return None

if __name__ == "__main__":
    addr = input("輸入中文地址: ").strip()
    result = geocode_nominatim_debug(addr)
    if result:
        print(f"地址: {addr}")
        print(f"緯度: {result[0]}, 經度: {result[1]}")
    else:
        print("找不到座標或發生錯誤。請查看 STDERR 的 debug 訊息以了解詳情。")