from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

game_addresses = []

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    address = data.get('address')
    if address and address not in game_addresses:
        game_addresses.append(address)
        print(f"Registered new game address: {address}")
    return jsonify({"status": "success", "addresses": game_addresses})

@app.route('/get_addresses', methods=['GET'])
def get_addresses():
    return jsonify({"addresses": game_addresses})

if __name__ == '__main__':
    app.run(host='192.168.1.120', port=49990)
