from flask import Flask, Response, request
from flask_cors import CORS
import requests, re, json, threading, time, hashlib
from urllib.parse import quote
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

SUPPORTED_DOMAINS = [
    "linkvertise.com",
    "direct-link.net",
    "link-hub.net",
    "link-target.net",
    "link-center.net",
    "link-to.net"
]

LOOT_DOMAINS = [
    "lootdest.com/s?",
    "links-loot.com/s?",
    "linksloot.net/s?",
    "lootdest.info/s?",
    "lootdest.org/s?",
    "loot-link.com/s?",
    "loot-links.com/s?",
    "lootlink.org/s?",
    "lootlinks.co/s?"
]

UNIPLEX_DOMAINS = [
    "mboost.me",
    "rekonise.com",
    "rekonise.org",
    "sub4unlock.pro",
    "sub4unlock.com",
    "linkunlocker.com",
    "sub2unlock.com",
    "sub2unlock.top",
    "sub2get.com",
    "socialwolvez.com",
    "go.linkify.ru",
    "boost.ink",
    "link-unlock.com",
    "krnl-ios.com",
    "deltaios-executor.com",
    "nirbytes.com/sub2unlock/",
    "scriptpastebins.com/",
    "robloxscripts.gg/",
    "linkzy.space/",
    "neoxsoftworks.eu",
    "www.jinkx.pro",
    "ntt-hub.xyz/key/get-key?hwid="
]

PASTERSO_DOMAINS = [
    "paster.so"
]

ORIGIN_WHITELIST = {
    "archub.dev": ["link-to.net"],
    "keyrblx.com": [
        "linkvertise.com",
        "direct-link.net",
        "link-hub.net",
        "link-target.net",
        "link-center.net",
        "link-to.net"
    ]
}

GITHUB_URL = "https://github.com/BaconButPro/ron12373/raw/Premium/Install-Userscript/Bypass.user.js"
SUB_API = "http://156.226.175.176:13190"
API_BYPASS = "https://krnl.cloak-x.net/bypass"
LOOT_API_BYPASS = "http://87.106.208.203:10211/bypass"
UNIPLEX_API_BYPASS = "https://sad2n2yd.herindz.click/bypass"
PASTERSO_API_BYPASS = "http://156.226.175.176:3000/pasterso"
API_BYPASS_KEY = "buicon2011"
SECRET_TOKEN = "BeaconHub200K@ThankYou"

# FREE KEY
FREE_KEY = "BaconButProPremiumTrial"

cached_keys = set()
cache_last_updated = None
cache_lock = threading.Lock()
CACHE_DURATION = 60

def handle_connection_error(endpoint_name):
    """Helper function to handle connection errors uniformly"""
    print(f"[CONNECTION ERROR] Failed to connect to {endpoint_name}")
    return Response(
        json.dumps({"status": "error", "message": "Failed to connect server"}, separators=(",", ":")),
        mimetype="application/json",
        status=500
    )

def get_client_ip():
    ip = request.headers.get("CF-Connecting-IP") \
         or request.headers.get("True-Client-IP") \
         or request.headers.get("X-Real-IP") \
         or request.headers.get("X-Forwarded-For") \
         or request.remote_addr
    if ip and "," in ip:
        ip = ip.split(",")[0].strip()
    return ip.strip()

def fetch_keys():
    """Fetch keys from SUB_API and update cache"""
    global cached_keys, cache_last_updated
    
    try:
        print(f"[CACHE] Fetching keys from {SUB_API}/key-list")
        response = requests.get(f"{SUB_API}/key-list", timeout=10)
        response.raise_for_status()
        
        with cache_lock:
            cached_keys = set(response.text.splitlines())
            cache_last_updated = datetime.now()
            
        print(f"[CACHE] Successfully cached {len(cached_keys)} keys at {cache_last_updated}")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"[CACHE ERROR] Failed to fetch keys: {e}")
        return False
    except Exception as e:
        print(f"[CACHE ERROR] Unexpected error: {e}")
        return False

def get_cached_keys():
    """Get keys from cache, fetch if expired or empty"""
    global cached_keys, cache_last_updated
    
    with cache_lock:
        current_time = datetime.now()
        
        if (not cached_keys or 
            cache_last_updated is None or 
            current_time - cache_last_updated > timedelta(seconds=CACHE_DURATION)):
            
            print("[CACHE] Cache expired or empty, fetching new keys")
        else:
            print(f"[CACHE] Using cached keys ({len(cached_keys)} keys, age: {(current_time - cache_last_updated).total_seconds():.1f}s)")
            return cached_keys.copy()
            
    fetch_keys()
    
    with cache_lock:
        return cached_keys.copy()

def start_cache_updater():
    """Background thread to update cache every minute"""
    def cache_updater():
        while True:
            time.sleep(CACHE_DURATION)
            fetch_keys()
    
    cache_thread = threading.Thread(target=cache_updater, daemon=True)
    cache_thread.start()
    print("[CACHE] Started background cache updater")

def verify_token(url, token, timestamp):
    """Verify SHA-256 token for URL with timestamp (valid for 30 seconds)"""
    if not token or not timestamp:
        return False
    
    try:
        # Check if timestamp is within 30 seconds
        request_time = int(timestamp)
        current_time = int(time.time())
        time_diff = abs(current_time - request_time)
        
        if time_diff > 30:  # Token expired after 30 seconds
            print(f"[TOKEN] Expired - Time diff: {time_diff}s")
            return False
        
        # Verify token: SHA256(url + timestamp + secret)
        raw = (url + str(timestamp) + SECRET_TOKEN).encode()
        expected_hash = hashlib.sha256(raw).hexdigest()
        return expected_hash == token
        
    except (ValueError, TypeError) as e:
        print(f"[TOKEN] Invalid timestamp format: {e}")
        return False

def validate_origin(url, origin):
    """
    Validate if origin is allowed:
    - If origin is from SUPPORTED_DOMAINS => chỉ cho phép URL có cùng domain loại đó
    - Nếu origin == domain URL => cho qua
    - Nếu origin có trong ORIGIN_WHITELIST => chỉ cho URL từ domain mapping
    - Ngược lại => False
    """
    if not origin:
        return False

    origin_clean = origin.replace("https://", "").replace("http://", "").lower()

    from urllib.parse import urlparse
    try:
        parsed_url = urlparse(url)
        url_domain = parsed_url.netloc.lower()
    except:
        return False

    for supported_domain in SUPPORTED_DOMAINS:
        if origin_clean == supported_domain or origin_clean.endswith("." + supported_domain):
            return url_domain == supported_domain or url_domain.endswith("." + supported_domain)

    if origin_clean == url_domain or origin_clean.endswith("." + url_domain):
        return True

    allowed_domains = ORIGIN_WHITELIST.get(origin_clean)
    if allowed_domains:
        for allowed_domain in allowed_domains:
            if url_domain == allowed_domain or url_domain.endswith("." + allowed_domain):
                return True
        return False

    return False

# ============= ENDPOINT CŨ =============

@app.route("/siu", methods=["GET"])
def get_version():
    try:
        response = requests.get(GITHUB_URL, timeout=10)
        response.raise_for_status()
        content = response.text
        match = re.search(r"@version\s+([0-9]+\.[0-9]+\.[0-9]+)", content)
        if match:
            version = match.group(1)
            return Response(json.dumps({"Version": version}, separators=(",", ":")), mimetype="application/json")
        else:
            return Response(json.dumps({"error": "Version not found"}, separators=(",", ":")), mimetype="application/json"), 404
    except requests.exceptions.RequestException:
        return handle_connection_error("GitHub")
    except Exception as e:
        return Response(json.dumps({"error": str(e)}, separators=(",", ":")), mimetype="application/json"), 500

@app.route("/vn", methods=["GET"])
def access():
    key = request.args.get("BBP")
    if not key:
        return Response(
            json.dumps({"error": "Missing key"}, separators=(",", ":")),
            mimetype="application/json",
        ), 400
    
    try:
        ip = get_client_ip()
        print(f"[ACCESS] Client IP: {ip}")
        
        # Check if it's free key
        if key == FREE_KEY:
            print(f"[ACCESS] Free key used: {FREE_KEY}")
            # Trả về response đúng định dạng cũ
            return Response(
                json.dumps({"status": "key valid", "whitelist": "IP Whitelisted"}, separators=(",", ":")),
                mimetype="application/json",
            )
        
        keys = get_cached_keys()
        
        if key not in keys:
            return Response(
                json.dumps({"status": "invalid key"}, separators=(",", ":")),
                mimetype="application/json",
            ), 403
        
        try:
            r_check = requests.get(f"{SUB_API}/check-access?ip={ip}&key={key}", timeout=15)
            return Response(r_check.text, status=r_check.status_code, mimetype="application/json")
        except requests.exceptions.RequestException:
            return handle_connection_error("SUB_API check-access")
            
    except Exception as e:
        print(f"[ACCESS ERROR] {e}")
        return Response(
            json.dumps({"error": "Internal Server Error"}, separators=(",", ":")),
            mimetype="application/json",
        ), 500

@app.route("/cache-status", methods=["GET"])
def cache_status():
    """Debug endpoint to check cache status"""
    with cache_lock:
        return Response(
            json.dumps({
                "cached_keys_count": len(cached_keys),
                "last_updated": cache_last_updated.isoformat() if cache_last_updated else None,
                "cache_age_seconds": (datetime.now() - cache_last_updated).total_seconds() if cache_last_updated else None
            }, separators=(",", ":")),
            mimetype="application/json"
        )
    
@app.route("/install-userscript/<key>/BaconPremium.user.js", methods=["GET"])
def install_userscript(key):
    try:
        response = requests.get(GITHUB_URL, timeout=30)
        response.raise_for_status()
        content = response.text
        
        pattern = r"function key\(\) \{\s*return '[^']*';\s*// Your Access Key\s*\}"
        replacement = f"function key() {{\n    return '{key}'; // Your Access Key\n}}"
        
        modified_content = re.sub(pattern, replacement, content)
        
        if modified_content == content:
            pattern2 = r"(function key\(\) \{\s*return\s*')[^']*(';\s*// Your Access Key\s*\})"
            replacement2 = f"\\g<1>{key}\\g<2>"
            modified_content = re.sub(pattern2, replacement2, content)
        
        if modified_content == content:
            pattern3 = r"return\s*'[^']*';\s*//\s*Your Access Key"
            replacement3 = f"return '{key}'; // Your Access Key"
            modified_content = re.sub(pattern3, replacement3, content)
        
        return Response(modified_content, mimetype="application/javascript")
        
    except requests.exceptions.RequestException:
        return Response(f"// Error: Failed to connect server", mimetype="application/javascript"), 500
    except Exception as e:
        return Response(f"// Error loading userscript: {str(e)}", mimetype="application/javascript"), 500

# ============= ENDPOINT MỚI VỚI TOKEN =============

@app.route("/get-time", methods=["GET"])
def get_time():
    """Get current server time in Unix timestamp and ISO format"""
    now = datetime.utcnow()
    return Response(
        json.dumps({
            "unix": int(time.time()),
            "iso": now.isoformat() + "Z"
        }, separators=(",", ":")),
        mimetype="application/json"
    )

@app.route("/kwad", methods=["GET"])
def bypass():
    """Bypass endpoint with SHA-256 token verification"""
    url = request.args.get("os")
    token = request.args.get("token")
    timestamp = request.args.get("timestamp")
    
    # Verify token first
    if not url:
        print("[FAILED] Missing URL parameter")
        return Response(json.dumps({"error": "Missing url"}, separators=(",", ":")), mimetype="application/json"), 400
    
    if not verify_token(url, token, timestamp):
        print(f"[FAILED] Invalid or expired token for URL: {url}")
        return Response(json.dumps({"error": "Invalid or expired token"}, separators=(",", ":")), mimetype="application/json"), 403

    is_loot_domain = any(domain in url for domain in LOOT_DOMAINS)
    is_supported_domain = any(domain in url for domain in SUPPORTED_DOMAINS)
    is_uniplex_domain = any(domain in url for domain in UNIPLEX_DOMAINS)
    is_pasterso_domain = any(domain in url for domain in PASTERSO_DOMAINS)

    if not (is_loot_domain or is_supported_domain or is_uniplex_domain or is_pasterso_domain):
        print(f"[FAILED] Unsupported domain: {url}")
        return Response(json.dumps({"error": "unsupported"}, separators=(",", ":")), mimetype="application/json"), 400

    user_agent = request.headers.get("User-Agent")
    if not user_agent:
        print("[FAILED] Invalid HMAC - Missing User-Agent header")
        return Response(json.dumps({"error": "Missing Auth Token API (HMAC)"}, separators=(",", ":")), mimetype="application/json"), 401

    origin = request.headers.get("Origin") or request.headers.get("Referer")
    if not validate_origin(url, origin):
        print(f"[FAILED] Invalid HMAC - Origin validation failed. Origin: {origin}, URL: {url}")
        return Response(json.dumps({"error": "Missing Auth Token API (HMAC)"}, separators=(",", ":")), mimetype="application/json"), 403

    accept_lang = request.headers.get("Accept-Language", "")
    if ";;" not in accept_lang:
        print(f"[FAILED] Invalid HMAC - Accept-Language does not contain ';;'. Received: {accept_lang}")
        return Response(json.dumps({"error": "Missing Auth Token API (HMAC)"}, separators=(",", ":")), mimetype="application/json"), 401

    accept_header = request.headers.get("Accept", "")
    if "//" not in accept_header:
        print(f"[FAILED] Invalid HMAC - Accept missing '//'. Received: {accept_header}")
        return Response(json.dumps({"error": "Missing Auth Token API (HMAC)"}), mimetype="application/json"), 401

    api_key = request.headers.get("X-Auth-Token")
    if not api_key:
        print("[FAILED] Invalid HMAC - Missing X-Auth-Token header")
        return Response(json.dumps({"error": "Missing Auth Token API (HMAC)"}, separators=(",", ":")), mimetype="application/json"), 401

    client_ip = get_client_ip()
    
    # Check if it's free key
    if api_key == FREE_KEY:
        print(f"[FREE KEY] Free key used for URL: {url}, IP: {client_ip}")
        # Bypass all IP and key checks for free key
        # Không cần kiểm tra key-list và verify-check
        print(f"[PASS] Security check passed for IP: {client_ip}, API key: {api_key} (FREE KEY), URL: {url}")
    else:
        # Normal key verification
        try:
            try:
                r_keys = requests.get(f"{SUB_API}/key-list", timeout=30)
            except requests.exceptions.RequestException:
                print("[FAILED] Invalid HMAC - Cannot connect to SUB_API key-list")
                return handle_connection_error("SUB_API key-list")

            if api_key not in r_keys.text.splitlines():
                print(f"[FAILED] Invalid HMAC - API key not found in key-list: {api_key}")
                return Response(json.dumps({"error": "Missing Auth Token API (HMAC)"}, separators=(",", ":")), mimetype="application/json"), 401

            try:
                r_verify = requests.get(f"{SUB_API}/verify-check?ip={client_ip}&key={api_key}", timeout=30)
            except requests.exceptions.RequestException:
                print(f"[FAILED] Invalid HMAC - Cannot connect to SUB_API verify-check for IP: {client_ip}")
                return handle_connection_error("SUB_API verify-check")

            try:
                verify_data = r_verify.json()
            except ValueError:
                print(f"[FAILED] Invalid HMAC - Invalid JSON response from verify-check. Response: {r_verify.text}")
                return Response(json.dumps({"error": "Missing Auth Token API (HMAC)"}, separators=(",", ":")), mimetype="application/json"), 401

            if verify_data.get("access") != "True":
                print(f"[FAILED] Invalid HMAC - Access denied for IP: {client_ip}, API key: {api_key}. Response: {verify_data}")
                return Response(json.dumps({"error": "Missing Auth Token API (HMAC)"}, separators=(",", ":")), mimetype="application/json"), 401
        except Exception as e:
            print(f"[FAILED] Invalid HMAC - Exception during verification: {str(e)}")
            return Response(json.dumps({"error": str(e)}, separators=(",", ":")), mimetype="application/json"), 500

        print(f"[PASS] Security check passed for IP: {client_ip}, API key: {api_key}, URL: {url}")

    if is_pasterso_domain:
        try:
            encoded_url = quote(url, safe="")
            r_bypass = requests.get(f"{PASTERSO_API_BYPASS}?url={encoded_url}", timeout=30)
            return Response(r_bypass.text, mimetype="application/json")
        except requests.exceptions.RequestException:
            return handle_connection_error("PASTERSO_API")
        except Exception as e:
            return Response(json.dumps({"error": str(e)}, separators=(",", ":")), mimetype="application/json"), 500

    if is_uniplex_domain:
        try:
            encoded_url = quote(url, safe="")
            r_bypass = requests.get(f"{UNIPLEX_API_BYPASS}?url={encoded_url}", timeout=30)
            return Response(r_bypass.text, mimetype="application/json")
        except requests.exceptions.RequestException:
            return handle_connection_error("UNIPLEX_API")
        except Exception as e:
            return Response(json.dumps({"error": str(e)}, separators=(",", ":")), mimetype="application/json"), 500

    if is_loot_domain:
        try:
            encoded_url = quote(url, safe="")
            r_bypass = requests.get(f"{LOOT_API_BYPASS}?url={encoded_url}", timeout=110)
            return Response(r_bypass.text, mimetype="application/json")
        except requests.exceptions.RequestException:
            return handle_connection_error("LOOT_API")
        except Exception as e:
            return Response(json.dumps({"error": str(e)}, separators=(",", ":")), mimetype="application/json"), 500

    if is_supported_domain:
        try:
            encoded_url = quote(url, safe="")
            r_bypass = requests.get(f"{API_BYPASS}?url={encoded_url}&apikey={API_BYPASS_KEY}", timeout=30)
            return Response(r_bypass.text, mimetype="application/json")
        except requests.exceptions.RequestException:
            return handle_connection_error("API_BYPASS")
        except Exception as e:
            return Response(json.dumps({"error": str(e)}, separators=(",", ":")), mimetype="application/json"), 500
    
@app.route("/ip", methods=["GET"])
def show_ip():
    ip = get_client_ip()
    return Response(ip, mimetype="text/plain")

if __name__ == "__main__":
    print("[STARTUP] Initializing key cache...")
    fetch_keys()
    
    start_cache_updater()
    app.run(host="0.0.0.0", port=5000, debug=True)
