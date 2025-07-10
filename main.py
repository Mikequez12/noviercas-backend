from flask import Flask, send_from_directory, abort, jsonify, request
import json
from datetime import datetime, timedelta
import random
import os

from spam import send_verification
from flask_cors import CORS


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


@app.route('/admin', methods=['POST','OPTIONS'])
def admin():
  if request.method == 'OPTIONS':
        return 'preflight ok', 200, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'PUT,DELETE',
            'Access-Control-Allow-Headers': 'content-type'
        }
  exp_tokens()
  if (request.get_json()['password'] == '#noviercas'):
    with open('tokens.json','r',encoding='utf-8') as file:
      return jsonify({"tokens":json.load(file)})
  else:
    abort(405)

def exp_tokens():
    try:
        with open('tokens.json', 'r', encoding='utf-8') as file:
            tokens = json.load(file)
    except json.JSONDecodeError:
        tokens = {}
    
    new_tokens = {}
    now = datetime.utcnow()
    
    for token, data in tokens.items():
        exp_time = datetime.fromisoformat(data['exp'])
        if now < exp_time:
            new_tokens[token] = data
    
    with open('tokens.json', 'w') as file:
        json.dump(new_tokens, file)

if not os.path.exists('tokens.json'):
    with open('tokens.json', 'w') as f:
        json.dump({}, f)
  
@app.route('/token', methods=['POST','OPTIONS'])
def handle_token():
    if request.method == 'OPTIONS':
        return 'preflight ok', 200, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'PUT,DELETE',
            'Access-Control-Allow-Headers': 'content-type'
        }
    exp_tokens()
    
    with open('tokens.json') as file:
        actual_passwords = json.load(file)
        
    new_password = None
    max_attempts = 1000
    
    for _ in range(max_attempts):
        candidate = random.randint(0, 99999999)
        if str(candidate) not in actual_passwords:
            new_password = candidate
            break
    if new_password is None:
        abort(500, 'ERROR: Could not generate unique token')
        
    new_file = actual_passwords.copy()
    expiration = datetime.utcnow() + timedelta(minutes=5)
    new_file[str(new_password)] = {
        'exp': expiration.isoformat(),
        'dat': {
            'dsr':request.get_json()['dsr']
        }
    }
    
    with open('tokens.json', 'w') as file:
        json.dump(new_file, file)
    
    print(new_file)
    
    """
return jsonify({
        "token": str(new_password),
        "expires-in": expiration.isoformat()
    })

@app.route('/send', methods=['POST','OPTIONS'])
def send_data():
    if request.method == 'OPTIONS':
        return 'preflight ok', 200, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'PUT,DELETE',
            'Access-Control-Allow-Headers': 'content-type'
        }
    """
    name = request.get_json()['name']
    token = str(new_password)
    mail = request.get_json()['mail']
    
    app.logger.info(send_verification(name,token,mail))

    return jsonify({"ok":True})


@app.route('/check', methods=['POST','OPTIONS'])
def check():
  if request.method == 'OPTIONS':
        return 'preflight ok', 200, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'PUT,DELETE',
            'Access-Control-Allow-Headers': 'content-type'
        }
  exp_tokens()
  with open('tokens.json','r',encoding='utf-8') as file:
    v = json.load(file).get(request.get_json()['token'],False)
  if not v:
    return jsonify({"ok":False})
  return jsonify({"ok":True,"values":v})
  
  
def exp_tokens():
    try:
        with open('tokens.json', 'r', encoding='utf-8') as file:
            tokens = json.load(file)
    except json.JSONDecodeError:
        tokens = {}
    
    new_tokens = {}
    now = datetime.utcnow()
    
    for token, data in tokens.items():
        exp_time = datetime.fromisoformat(data['exp'])
        if now < exp_time:
            new_tokens[token] = data
    
    with open('tokens.json', 'w') as file:
        json.dump(new_tokens, file)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render la define automáticamente
    app.run(host="0.0.0.0", port=port)         # ← host correcto