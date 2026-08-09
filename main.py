from flask import Flask, send_from_directory, abort, jsonify, request
import json
from datetime import datetime, timedelta
import random
import os

from spam import send_verification
from flask_cors import CORS

import requests




def get_users():
    values = requests.get(
        'https://sheets.googleapis.com/v4/spreadsheets/1RCxdryrlsUn37VZz5UlndUcFWjCUDElhGQMJLTfx6rk/values/signup?key=AIzaSyCPoCo9JcBf6_p7JqlPDZ_6frBODdw4EAI'
    ).json().get('values')

    headers = values[0][10:]
    data = values[1:]
    data = [v[10:] for v in data if len(v) != 0]

    response = {}

    for row in data:
        response[row[0]] = {}

        for i, k in enumerate(headers):
            if i >= len(row):
                continue

            response[row[0]][k] = row[i]

    return response


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/ping')
def ping():
    return 'pong'

@app.route('/admin', methods=['POST', 'OPTIONS'])
def admin():
    if request.method == 'OPTIONS':
        return 'preflight ok', 200, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST,OPTIONS',
            'Access-Control-Allow-Headers': 'content-type'
        }

    exp_tokens()

    if request.get_json()['password'] == '#noviercas':
        with open('tokens.json', 'r', encoding='utf-8') as file:
            return jsonify({"tokens": json.load(file)})
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


"""
@app.route('/token', methods=['POST','OPTIONS'])
def handle_token():
    if request.method == 'OPTIONS':
        return 'preflight ok', 200, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST,OPTIONS',
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
            'dsr': request.get_json()['dsr']
        }
    }

    with open('tokens.json', 'w') as file:
        json.dump(new_file, file)

    print(new_file)

    return jsonify({
        "ok": True,
        "token": str(new_password),
        "expires-in": expiration.isoformat()
    })


@app.route('/send', methods=['POST','OPTIONS'])
def send_data():
    if request.method == 'OPTIONS':
        return 'preflight ok', 200, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST,OPTIONS',
            'Access-Control-Allow-Headers': 'content-type'
        }

    name = request.get_json()['name']
    token = str(new_password)
    mail = request.get_json()['mail']

    app.logger.info(send_verification(name, token, mail))

    return jsonify({"ok": True})
"""


@app.route('/token', methods=['POST', 'OPTIONS'])  # login
def login():
    if request.method == 'OPTIONS':
        return 'preflight ok', 200

    data = request.get_json()

    dsr = data['dsr']

    # Buscar usuario
    user = get_users().get(dsr)

    if not user:
        return jsonify({"ok": True, "error": "Not found"}), 404

    exp_tokens()

    # Generar token
    with open('tokens.json', 'r', encoding='utf-8') as file:
        actual_tokens = json.load(file)

    for _ in range(1000):
        token = str(random.randint(0, 99999999))

        if token not in actual_tokens:
            break
    else:
        return jsonify({"ok": False}), 500

    expiration = datetime.utcnow() + timedelta(minutes=5)

    return "-",200

    actual_tokens[token] = {
        "exp": expiration.isoformat(),
        "dat": {
            "dsr": dsr
        }
    }

    with open('tokens.json', 'w', encoding='utf-8') as file:
        json.dump(actual_tokens, file)

    # Enviar correo DESDE EL BACKEND
    result = send_verification(
        user["name"],
        token,
        user["mail"]
    )

    if not result:
        # Opcional: eliminar el token si el correo falló
        del actual_tokens[token]

        with open('tokens.json', 'w', encoding='utf-8') as file:
            json.dump(actual_tokens, file)

        return jsonify({"ok": True}), 500

    return jsonify({"ok": True})


@app.route('/check', methods=['POST', 'OPTIONS'])
def check():
    if request.method == 'OPTIONS':
        return 'preflight ok', 200, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'PUT,DELETE',
            'Access-Control-Allow-Headers': 'content-type'
        }

    exp_tokens()

    with open('tokens.json', 'r', encoding='utf-8') as file:
        v = json.load(file).get(
            request.get_json()['token'],
            False
        )

    if not v:
        return jsonify({"ok": False})

    return jsonify({
        "ok": True,
        "values": v
    })


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
    app.run(host="0.0.0.0", port=port)
