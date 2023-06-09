import random
import json
import os
import threading
from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from flask import jsonify
from sqlalchemy import Column, Integer, String, Sequence
from sqlalchemy.ext.declarative import declarative_base
from apscheduler.schedulers.background import BackgroundScheduler


app = Flask(__name__)
CORS(app)


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


Base = declarative_base()


class HistoricoFinal(Base):
    __tablename__ = 'historico_final'
    id = Column(Integer, Sequence('historico_final_id_seq'), primary_key=True)
    idsession = Column(Integer)
    jogador1 = Column(Integer)
    jogador2 = Column(Integer)
    foi_vitoria = Column(Integer)


class Jogador(Base):
    __tablename__ = 'jogador'

    id = Column(Integer, primary_key=True)
    nome = Column(String)
    isactive = Column(Boolean, default=True)
    login = Column(String)
    senha = Column(String)
    email = Column(String)


class Fila(Base):
    __tablename__ = 'fila'

    id_usuario = Column(Integer, primary_key=True)
    jogador_nome = Column(String)
    peca = Column(String)
    tema = Column(String)


class Partida(Base):
    __tablename__ = 'partida'

    id_partida = Column(Integer, primary_key=True)
    id_usuario1 = Column(Integer)
    id_usuario2 = Column(Integer)


Base.metadata.create_all(engine)


class Cell:
    def __init__(self, classList, x, y):
        self.classList = classList
        self.x = x
        self.y = y


# Inicialize last_move como um dicionário vazio
last_move = {}
session_id = 0
file_path = "last_move.txt"


@app.route('/api/login', methods=['POST'])
def login():
    login = request.args.get('Login')
    senha = request.args.get('Senha')

    user = session.query(Jogador).filter_by(login=login, senha=senha).first()

    if user:
        # Incluir o ID do usuário no JSON de resposta
        print(user.id)
        return jsonify(status="success", user_id=user.id), 200
    else:
        return jsonify(status="fail"), 401


@app.route('/api/send-move', methods=['POST'])
def send_move():
    move = [Cell(**cell) for cell in request.json['move']]
    session_id = request.json.get('session_id')
    file_path = f"last_move_{session_id}.txt"

    try:
        with open(file_path, 'w') as file:
            file.write(json.dumps([cell.__dict__ for cell in move]))
        return "", 200
    except Exception as e:
        print(f"Error writing to file: {e}")
        return jsonify(status="error"), 500


@app.route('/api/send-audio', methods=['POST'])
def send_audio():
    session_id = request.json.get('session_id')
    print(session_id)
    audio_id = request.json['audio_id']
    print(audio_id)
    file_path = f"last_audio_{session_id}.txt"

    try:
        with open(file_path, 'w') as file:
            file.write(json.dumps(audio_id))
        return "", 200
    except Exception as e:
        print(f"Error writing to file: {e}")
        return jsonify(status="error"), 500


@app.route('/api/send-gif', methods=['POST'])
def send_gif():
    session_id = request.json.get('session_id')
    print(session_id)
    gif_id = request.json['gif_id']
    print(gif_id)
    file_path = f"last_gif_{session_id}.txt"

    try:
        with open(file_path, 'w') as file:
            file.write(json.dumps(gif_id))
        return "", 200
    except Exception as e:
        print(f"Error writing to file: {e}")
        return jsonify(status="error"), 500


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


def save_to_file(move, session_id):
    file_path = f"last_move_{session_id}.txt"
    try:
        if os.path.isfile(file_path):
            with open(file_path, 'r+') as file:
                file.seek(0)
                file.write(json.dumps([cell.__dict__ for cell in move]))
                file.truncate()
        else:
            with open(file_path, 'w') as file:
                file.write(json.dumps([cell.__dict__ for cell in move]))
        last_move[session_id] = [cell.__dict__ for cell in move]
    except Exception as e:
        print(f"Error writing to file: {e}")


@app.route('/api/check', methods=['POST'])
def get_move():
    session_id = request.json.get('session_id')
    file_path = f"last_move_{session_id}.txt"

    if session_id not in last_move or not os.path.exists(file_path):
        initial_state = [{"classList": ["cell", "piece-dog", "occupied-highlight"], "x": "0", "y": "0"}, {"classList": ["cell", "piece-dog", "occupied-highlight"], "x": "1", "y": "0"}, {"classList": ["cell", "piece-dog", "occupied-highlight"], "x": "2", "y": "0"}, {"classList": ["cell", "piece-dog", "occupied-highlight"], "x": "3", "y": "0"}, {"classList": ["cell", "piece-dog", "occupied-highlight"], "x": "4", "y": "0"}, {"classList": ["cell", "piece-dog", "occupied-highlight"], "x": "0", "y": "1"}, {"classList": ["cell", "piece-dog", "occupied-highlight"], "x": "1", "y": "1"}, {"classList": ["cell", "piece-dog", "occupied-highlight"], "x": "2", "y": "1"}, {"classList": ["cell", "piece-dog", "occupied-highlight"], "x": "3", "y": "1"}, {"classList": ["cell", "piece-dog", "occupied-highlight"], "x": "4", "y": "1"}, {"classList": ["cell", "piece-dog", "occupied", "occupied-highlight"], "x": "0", "y": "2"}, {"classList": ["cell", "highlight"], "x": "1", "y": "2"}, {"classList": ["cell", "piece-jaguar", "occupied",
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              "occupied-highlight"], "x": "2", "y": "2"}, {"classList": ["cell", "piece-dog", "occupied-highlight"], "x": "3", "y": "2"}, {"classList": ["cell", "piece-dog", "occupied-highlight"], "x": "4", "y": "2"}, {"classList": ["cell", "highlight"], "x": "0", "y": "3"}, {"classList": ["cell", "occupied-highlight"], "x": "1", "y": "3"}, {"classList": ["cell", "highlight", "piece-dog"], "x": "2", "y": "3"}, {"classList": ["cell"], "x": "3", "y": "3"}, {"classList": ["cell"], "x": "4", "y": "3"}, {"classList": ["cell", "highlight"], "x": "0", "y": "4"}, {"classList": ["cell", "highlight"], "x": "1", "y": "4"}, {"classList": ["cell", "highlight"], "x": "2", "y": "4"}, {"classList": ["cell"], "x": "3", "y": "4"}, {"classList": ["cell"], "x": "4", "y": "4"}, {"classList": ["cell"], "x": "1", "y": "5"}, {"classList": ["cell"], "x": "2", "y": "5"}, {"classList": ["cell"], "x": "3", "y": "5"}, {"classList": ["cell"], "x": "0", "y": "6"}, {"classList": ["cell"], "x": "2", "y": "6"}, {"classList": ["cell"], "x": "4", "y": "6"}]
        last_move[session_id] = [Cell(**cell) for cell in initial_state]

    load_from_file(file_path, session_id)

    if len(last_move[session_id]) == 0:
        return jsonify(status="no move"), 200

    response = jsonify(status="move available", move=[
                       cell.__dict__ for cell in last_move[session_id]])
    return response, 200


@app.route('/api/checkaudio', methods=['POST'])
def get_audio():
    session_id = request.json.get('session_id')
    file_path = f"last_audio_{session_id}.txt"

    f = open(file_path)
    audio_id = f.read()

    if audio_id == "0":
        response = jsonify(status="no audio", audio=0)
    else:
        response = jsonify(status="audio available", audio=audio_id)

    return response, 200


@app.route('/api/checkgif', methods=['POST'])
def get_gif():
    session_id = request.json.get('session_id')
    file_path = f"last_gif_{session_id}.txt"

    f = open(file_path)
    gif_id = f.read()

    if gif_id == "0":
        response = jsonify(status="no gif", gif=0)
    else:
        response = jsonify(status="gif available", gif=gif_id)

    return response, 200


def save_to_file(move, session_id):
    file_path = f"last_move_{session_id}.txt"
    try:
        with open(file_path, 'w') as file:
            json.dump([cell.__dict__ for cell in move], file)
        last_move[session_id] = [cell.__dict__ for cell in move]
    except Exception as e:
        print(f"Error writing to file: {e}")


def load_from_file(file_path, session_id):
    if not os.path.isfile(file_path):
        print(f"File {file_path} does not exist. Creating file.")
        initial_state = [{"classList": ["cell", "piece-dog", "occupied-highlight"], "x": "0", "y": "0"}, {"classList": ["cell", "piece-dog", "occupied-highlight"], "x": "1", "y": "0"}, {"classList": ["cell", "piece-dog", "occupied-highlight"], "x": "2", "y": "0"}, {"classList": ["cell", "piece-dog", "occupied-highlight"], "x": "3", "y": "0"}, {"classList": ["cell", "piece-dog", "occupied-highlight"], "x": "4", "y": "0"}, {"classList": ["cell", "piece-dog", "occupied-highlight"], "x": "0", "y": "1"}, {"classList": ["cell", "piece-dog", "occupied-highlight"], "x": "1", "y": "1"}, {"classList": ["cell", "piece-dog", "occupied-highlight"], "x": "2", "y": "1"}, {"classList": ["cell", "piece-dog", "occupied-highlight"], "x": "3", "y": "1"}, {"classList": ["cell", "piece-dog", "occupied-highlight"], "x": "4", "y": "1"}, {"classList": ["cell", "piece-dog", "occupied", "occupied-highlight"], "x": "0", "y": "2"}, {"classList": ["cell", "highlight"], "x": "1", "y": "2"}, {"classList": ["cell", "piece-jaguar", "occupied",
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              "occupied-highlight"], "x": "2", "y": "2"}, {"classList": ["cell", "piece-dog", "occupied-highlight"], "x": "3", "y": "2"}, {"classList": ["cell", "piece-dog", "occupied-highlight"], "x": "4", "y": "2"}, {"classList": ["cell", "highlight"], "x": "0", "y": "3"}, {"classList": ["cell", "occupied-highlight"], "x": "1", "y": "3"}, {"classList": ["cell", "highlight", "piece-dog"], "x": "2", "y": "3"}, {"classList": ["cell"], "x": "3", "y": "3"}, {"classList": ["cell"], "x": "4", "y": "3"}, {"classList": ["cell", "highlight"], "x": "0", "y": "4"}, {"classList": ["cell", "highlight"], "x": "1", "y": "4"}, {"classList": ["cell", "highlight"], "x": "2", "y": "4"}, {"classList": ["cell"], "x": "3", "y": "4"}, {"classList": ["cell"], "x": "4", "y": "4"}, {"classList": ["cell"], "x": "1", "y": "5"}, {"classList": ["cell"], "x": "2", "y": "5"}, {"classList": ["cell"], "x": "3", "y": "5"}, {"classList": ["cell"], "x": "0", "y": "6"}, {"classList": ["cell"], "x": "2", "y": "6"}, {"classList": ["cell"], "x": "4", "y": "6"}]
        last_move[session_id] = [Cell(**cell) for cell in initial_state]

        with open(file_path, 'w') as file:
            file.write(json.dumps(
                [cell.__dict__ for cell in last_move[session_id]]))

    try:
        with open(file_path, 'r') as file:
            data = file.read()
            if data:
                last_move[session_id] = [Cell(**cell)
                                         for cell in json.loads(data)]
            else:
                print("File is empty. No move available.")
    except Exception as e:
        print(f"Error reading from file: {e}")

    # Agora, recupere o movimento do dicionário last_move
    move = last_move.get(session_id)
    return move


@app.route('/api/queue', methods=['POST'])
def add_to_queue():
    session = Session()  # Crie a sessão SQLAlchemy
    try:
        data = request.get_json()
        jogador = int(data.get('id_usuario'))
        tema = data.get('tema')
        peca = data.get('peca')

        with session.begin():
            # Verificar se já existe um registro para este usuário na fila
            fila_existente = session.query(Fila).filter(
                Fila.id_usuario == jogador).first()

            if fila_existente:
                # Atualizar o registro existente
                fila_existente.peca = peca
                fila_existente.tema = tema
            else:
                # Criar um novo registro
                new_queue = Fila(id_usuario=jogador, peca=peca, tema=tema)
                session.add(new_queue)

        session.commit()  # Confirme as alterações

        return jsonify(status="success"), 200
    except Exception as e:
        session.rollback()  # Desfaça as alterações em caso de exceção
        print(f"Error adding to queue: {e}")
        return jsonify(status="fail"), 500
    finally:
        session.close()  # Encerre a sessão


@app.route('/api/check_game_status', methods=['POST'])
def check_game_status():
    id_usuario = request.get_json().get('id_usuario')

    partida = session.query(Partida).filter((Partida.id_usuario1 == id_usuario) | (
        Partida.id_usuario2 == id_usuario)).first()

    if partida:
        session_id = partida.id_partida
        # Retorna o ID da partida, id_usuario1 e id_usuario2 se uma partida for encontrada
        return jsonify(status="success", session_id=partida.id_partida, id_usuario1=partida.id_usuario1, id_usuario2=partida.id_usuario2), 200
    else:
        return jsonify(status="fail"), 404


@app.route('/api/end_game', methods=['POST'])
def end_game():
    data = request.get_json()

    # Pega os dados enviados na requisição
    session_id = data.get('session_id')
    jogador1 = data.get('jogador1')
    jogador2 = data.get('jogador2')
    vitoria = data.get('vitoria')

    # Cria um novo registro de partida
    new_record = HistoricoFinal(id=session_id, jogador1=jogador1,
                                jogador2=jogador2, foi_vitoria=vitoria)

    # Adiciona e confirma as alterações no banco de dados
    session.add(new_record)
    session.commit()

    return jsonify(status="success"), 200


@app.route('/api/vitorias', methods=['POST'])
def obter_vitorias():
    jogador_id = request.json.get('jogador_id')

    # Consultar o banco de dados para obter o número de vitórias do jogador
    numero_vitorias = session.query(HistoricoFinal).filter_by(
        foi_vitoria=jogador_id).count()

    return jsonify(numero_vitorias=numero_vitorias)


def create_game_party():
    fila = session.query(Fila).all()
    temas = set()

    for jogador in fila:
        temas.add(jogador.tema)

    for tema in temas:
        jogadores_tema = session.query(Fila).filter_by(tema=tema).all()

        if len(jogadores_tema) >= 2:
            pecas = set()

            for jogador in jogadores_tema:
                pecas.add(jogador.peca)

            if len(pecas) >= 2:
                # Criar partida
                id_partida = random.randint(1000, 9999)

                partida = Partida(
                    id_partida=id_partida, id_usuario1=jogadores_tema[0].id_usuario, id_usuario2=jogadores_tema[1].id_usuario)
                session.add(partida)
                session.commit()

                # Remover jogadores da fila
                for jogador in jogadores_tema:
                    session.delete(jogador)
                session.commit()


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=create_game_party, trigger="interval", seconds=1)
    scheduler.start()


if __name__ == "__main__":
    threading.Thread(target=start_scheduler).start()
    app.run(port=5003)
