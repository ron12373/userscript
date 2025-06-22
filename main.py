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
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.92 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.178 Safari/537.36",
    "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.129 Safari/537.36"
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

def get_stages(session_url):
    try:
        check_api_url = f"http://87.106.100.210:6410/api/check-session?url={session_url}"
        headers = {
            'User-Agent': random.choice(user_agents)
        }
        response = requests.get(check_api_url, headers=headers, timeout=10)
        data = response.json()

        if data.get('error') == 'invalid-session':
            return {'error': 'invalid-session', 'message': data.get('userFacingMessage')}

        if data.get('success', False) and not data.get('authenticated', False):
            return data.get('stages', [])
    except:
        return None
    return None

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

    with ThreadPoolExecutor(max_workers=1) as executor:
        futures = [executor.submit(single_request) for _ in range(1)]
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

    with ThreadPoolExecutor(max_workers=1) as executor:
        futures = [executor.submit(single_request) for _ in range(1)]
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

    with ThreadPoolExecutor(max_workers=1) as executor:
        futures = [executor.submit(single_request) for _ in range(1)]
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
    stages = get_stages(session_url)
    if isinstance(stages, dict):
        if stages.get('error') == 'invalid-session':
            return jsonify({"status": "error", "message": stages.get('message', "Your session is invalid.")}), 200
    if not stages or not isinstance(stages, list):
        return jsonify({"status": "success","result":"Whitelist completed successfully"}), 400

    stages_completed = 0
    validated_tokens = []

    while stages_completed < len(stages):
        stage_id = stages[stages_completed]['uuid']
        success = False

        for attempt in range(3):
            print(f"Attempt {attempt + 1} for stage {stages_completed + 1}/{len(stages)}")
            init_token = initiate_stage(stage_id, session)
            if not init_token:
                print("Initiate failed.")
                continue

            sleep(5500)

            token_data = decode_token_data(init_token)
            referrer = 'https://linkvertise.com/'
            if 'loot-links' in token_data['link']:
                referrer = 'https://loot-links.com/'
            elif 'loot-link' in token_data['link']:
                referrer = 'https://loot-link.com/'

            validated_token = validate_stage(init_token, referrer, session)
            if validated_token:
                validated_tokens.append({'uuid': stage_id, 'token': validated_token})
                success = True
                break
            else:
                print("Validation failed.")

        if not success:
            return jsonify({"error": f"Stage {stages_completed + 1} failed after 3 attempts."}), 400

        stages_completed += 1
        print(f"{stages_completed}/{len(stages)} stages completed.")

    if authenticate(validated_tokens, session):
        duration = time.time() - start_time
        return jsonify({"status": "success", "result": "Whitelist completed successfully.", "time": duration}), 200
    else:
        return jsonify({"status": "error", "message": "Authentication failed during final step."}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
