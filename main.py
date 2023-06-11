from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": ["https://adugo-game-frontend-01.onrender.com", "https://adugo-game-frontend-prd.onrender.com"]}})

class Cell:
    def __init__(self, classList, x, y):
        self.classList = classList
        self.x = x
        self.y = y

last_move = []
file_path = "last_move.txt"

@app.route('/api/send-move', methods=['POST'])
def send_move():
    global last_move
    move = [Cell(**cell) for cell in request.json]
    last_move = move
    save_to_file(move)

    return "", 200

@app.route('/api/check', methods=['GET'])
def get_move():
    global last_move
    load_from_file()

    if len(last_move) == 0:
        return jsonify(status="no move"), 200

    response = jsonify(status="move available", move=[cell.__dict__ for cell in last_move])
    last_move = []
    
    return response, 200

def save_to_file(move):
    try:
        with open(file_path, 'w') as file:
            json.dump([cell.__dict__ for cell in move], file)
    except Exception as e:
        print(f"Error writing to file: {e}")

def load_from_file():
    global last_move
    if not os.path.isfile(file_path):
        print("File does not exist. No move available.")
        return
    
    try:
        with open(file_path, 'r') as file:
            data = file.read()
            if data:
                last_move = [Cell(**cell) for cell in json.loads(data)]
            else:
                print("File is empty. No move available.")
    except Exception as e:
        print(f"Error reading from file: {e}")

    
    try:
        with open(file_path, 'r') as file:
            last_move = [Cell(**cell) for cell in json.load(file)]
    except Exception as e:
        print(f"Error reading from file: {e}")

if __name__ == "__main__":
    app.run(port=5003)
