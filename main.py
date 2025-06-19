import requests
import json
import time
import base64
from urllib.parse import urlparse, parse_qs
import random
from flask import Flask, request, jsonify
from concurrent.futures import ThreadPoolExecutor, as_completed

app = Flask(__name__)

user_agents = [
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 9; SM-G960F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
]

def sleep(ms):
    time.sleep(ms / 1000)

def base64decode(str_data):
    missing_padding = len(str_data) % 4
    if missing_padding:
        str_data += '=' * (4 - missing_padding)
    str_data = str_data.replace("-", "+").replace("_", "/")
    return base64.b64decode(str_data).decode('utf-8')

def decode_token_data(token):
    data = token.split(".")[1]
    data = base64decode(data)
    return json.loads(data)

def get_stages(session):
    def single_request():
        headers = {
            'Android-Session': session,
            'User-Agent': random.choice(user_agents)
        }
        try:
            response = requests.get('https://api.codex.lol/v1/stage/stages', headers=headers, timeout=10)
            data = response.json()
            if data.get('success', False) and not data.get('authenticated', False):
                return data.get('stages', [])
        except:
            return None
        return None

    with ThreadPoolExecutor(max_workers=400) as executor:
        futures = [executor.submit(single_request) for _ in range(400)]
        for future in as_completed(futures):
            result = future.result()
            if result:
                return result  # Trả về kết quả đầu tiên thành công

    return []  # Nếu tất cả đều thất bại

def initiate_stage(stage_id, session):
    def single_request():
        headers = {
            'Android-Session': session,
            'User-Agent': random.choice(user_agents),
            'Content-Type': 'application/json'
        }
        body = json.dumps({"stageId": stage_id})
        try:
            response = requests.post('https://api.codex.lol/v1/stage/initiate', headers=headers, data=body, timeout=10)
            data = response.json()
            if data.get('success', False):
                return data.get('token')
        except:
            return None
        return None

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(single_request) for _ in range(20)]
        for future in as_completed(futures):
            result = future.result()
            if result:
                return result

    return None

def validate_stage(token, referrer, session):
    def single_request():
        headers = {
            'Android-Session': session,
            'User-Agent': random.choice(user_agents),
            'Content-Type': 'application/json',
            'Task-Referrer': referrer
        }
        body = json.dumps({"token": token})
        try:
            response = requests.post('https://api.codex.lol/v1/stage/validate', headers=headers, data=body, timeout=10)
            data = response.json()
            if data.get('success', False):
                return data.get('token')
        except:
            return None
        return None

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(single_request) for _ in range(20)]
        for future in as_completed(futures):
            result = future.result()
            if result:
                return result

    return None


def authenticate(validated_tokens, session):
    def single_request():
        headers = {
            'Android-Session': session,
            'User-Agent': random.choice(user_agents),
            'Content-Type': 'application/json'
        }
        body = json.dumps({"tokens": validated_tokens})
        try:
            response = requests.post('https://api.codex.lol/v1/stage/authenticate', headers=headers, data=body, timeout=10)
            data = response.json()
            if 'userFacingMessage' in data:
                print("API message: ", data['userFacingMessage'])
            if data.get('success', False):
                return True
        except:
            return None
        return None

    with ThreadPoolExecutor(max_workers=400) as executor:
        futures = [executor.submit(single_request) for _ in range(400)]
        for future in as_completed(futures):
            if future.result():
                return True

    return False

def extract_token_from_url(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    return query_params.get('token', [None])[0]

@app.route('/api/codex', methods=['GET'])
def start_process():
    session_url = request.args.get("url")
    session = extract_token_from_url(session_url)
    if not session:
        return jsonify({"error": "Invalid URL or token not found."}), 400

    start_time = time.time()
    stages = get_stages(session)
    if not stages:
        return jsonify({"error": "No stages available or authentication failed."}), 400

    stages_completed = 0
    validated_tokens = []

    while stages_completed < len(stages):
        stage_id = stages[stages_completed]['uuid']
        init_token = initiate_stage(stage_id, session)
        if not init_token:
            return jsonify({"error": "Stage initiation failed."}), 400

        sleep(6000)

        token_data = decode_token_data(init_token)
        referrer = 'https://linkvertise.com/'
        if 'loot-links' in token_data['link']:
            referrer = 'https://loot-links.com/'
        elif 'loot-link' in token_data['link']:
            referrer = 'https://loot-link.com/'

        validated_token = validate_stage(init_token, referrer, session)
        if validated_token:
            validated_tokens.append({'uuid': stage_id, 'token': validated_token})
        else:
            return jsonify({"error": "Stage validation failed."}), 400

        stages_completed += 1
        print(f"{stages_completed}/{len(stages)} stages completed.")

    if authenticate(validated_tokens, session):
        duration = time.time() - start_time
        return jsonify({"status": "success", "result": "Whitelist completed successfully.", "time": duration}), 200
    else:
        return jsonify({"error": "Authentication failed during final step."}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
