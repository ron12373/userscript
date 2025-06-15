import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import re
from flask import Flask, request, jsonify
import random
import threading

PROXY_SOURCES = [
    "https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&protocol=http",
    "https://www.proxy-list.download/api/v1/get?type=http",
    "https://api.openproxylist.xyz/http.txt",
    "https://www.proxyscan.io/download?type=http",
    "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt",
    "https://raw.githubusercontent.com/UserR3X/proxy-list/main/http.txt",
    "https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/http.txt",
    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/http.txt",
    "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
    "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt",
    "https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt",
    "https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/http.txt",
    "https://raw.githubusercontent.com/B4RC0DE-TM/proxy-list/main/HTTP.txt",
    "https://raw.githubusercontent.com/HyperBeats/proxy-list/main/http.txt",
    "https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/http/http.txt",
    "https://raw.githubusercontent.com/zevtyardt/proxy-list/main/http.txt",
    "https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/http.txt",
    "https://raw.githubusercontent.com/ObcbO/getproxy/master/http.txt"
]

FETCH_TIMEOUT = 10
VALIDATE_TIMEOUT = 2
MAX_WORKERS = 200

app = Flask(__name__)
proxy_lock = threading.Lock()
proxy_memory = set()
working_proxies = set()

def validate_and_store(proxy):
    try:
        res = requests.get("http://httpbin.org/ip", proxies={"http": proxy, "https": proxy}, timeout=VALIDATE_TIMEOUT)
        if res.status_code == 200:
            with proxy_lock:
                working_proxies.add(proxy)
    except:
        pass

def fetch_and_validate():
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for url in PROXY_SOURCES:
            try:
                res = requests.get(url, timeout=FETCH_TIMEOUT)
                if res.status_code == 200:
                    for line in res.text.strip().splitlines():
                        line = line.strip()
                        if not line:
                            continue
                        if '://' not in line:
                            line = f"http://{line}"
                        if re.match(r'^https?://\d{1,3}(\.\d{1,3}){3}:\d+$', line):
                            with proxy_lock:
                                if line not in proxy_memory:
                                    proxy_memory.add(line)
                                    executor.submit(validate_and_store, line)
            except:
                continue

@app.route("/proxy-request")
def proxy_request():
    with proxy_lock:
        proxies = list(working_proxies)

    random.shuffle(proxies)
    for proxy in proxies:
        try:
            res = requests.get("http://httpbin.org/ip", proxies={"http": proxy, "https": proxy}, timeout=VALIDATE_TIMEOUT)
            if res.status_code == 200:
                return jsonify({"status": "success", "proxy": proxy, "response": res.json()})
            else:
                with proxy_lock:
                    working_proxies.discard(proxy)
        except:
            with proxy_lock:
                working_proxies.discard(proxy)

    return jsonify({"status": "error", "message": "No working proxy found"}), 503

if __name__ == "__main__":
    print("[+] Starting fetch and validation thread...")
    threading.Thread(target=fetch_and_validate, daemon=True).start()
    print("[+] Running Flask 80...")
    app.run(host="0.0.0.0", port=80)