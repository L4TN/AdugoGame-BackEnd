import json
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": ["https://adugo-game-frontend-01.onrender.com",
                                             "https://adugo-game-frontend-prd.onrender.com", "http://127.0.0.1:5500"]}})

database = 'JogoOnca'
user = 'MasterOnca'
password = 'onca1020'
host = 'jogodaonca.cveloztfcqty.us-east-1.rds.amazonaws.com'
port = '5432'

database_url = f'postgresql://{user}:{password}@{host}:{port}/{database}'

engine = create_engine(database_url)

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


class Jogador(Base):
    __tablename__ = 'jogador'

    id = Column(Integer, primary_key=True)
    nome = Column(String)
    isactive = Column(Boolean, default=True)
    login = Column(String)
    senha = Column(String)
    email = Column(String)


Base.metadata.create_all(engine)


class Cell:
    def __init__(self, classList, x, y):
        self.classList = classList
        self.x = x
        self.y = y


last_move = []
file_path = "last_move.txt"


@app.route('/api/login', methods=['POST'])
def login():
    login = request.args.get('Login')
    senha = request.args.get('Senha')

    user = session.query(Jogador).filter_by(login=login, senha=senha).first()

    if user:
        # Incluir o ID do usuário no JSON de resposta
        return jsonify(status="success", user_id=user.id), 200
    else:
        return jsonify(status="fail"), 401


@app.route('/api/register', methods=['POST'])
def register():
    nome = request.args.get('Nome')
    login = request.args.get('Login')
    senha = request.args.get('Senha')
    email = request.args.get('Email')

    novo_jogador = Jogador(nome=nome, isactive=True,
                           login=login, senha=senha, email=email)
    session.add(novo_jogador)
    session.commit()

    return jsonify(status="success"), 201


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

    response = jsonify(status="move available", move=[
                       cell.__dict__ for cell in last_move])
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


if __name__ == "__main__":
    app.run(port=5003)
