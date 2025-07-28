from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/codex', methods=['GET'])
def bypass_redirect():
    original_url = request.args.get("url")
    if not original_url:
        return jsonify({"status": "error", "message": "Missing URL parameter"}), 400

    bypass_url = f"http://bypass.html?url={original_url}"
    return jsonify({"status": "success", "url": bypass_url}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
