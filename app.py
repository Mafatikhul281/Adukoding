from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit, join_room
import random
from lobby_manager import LobbyManager
from game_state_manager import GameStateManager
import eventlet
eventlet.monkey_patch()

app = Flask(__name__)
app.secret_key = "your_secret_key"
socketio = SocketIO(app, cors_allowed_origins="*")

lobbies = LobbyManager()
game_state = GameStateManager()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_lobby', methods=['POST'])
def create_lobby():
    username = request.form['username']
    room_code = lobbies.create_lobby(username)
    session['username'] = username
    session['room'] = room_code
    return redirect(url_for('waiting_room', room_code=room_code))

@app.route('/join_lobby', methods=['POST'])
def join_lobby():
    username = request.form['username']
    room_code = request.form['room_code']
    if lobbies.join_lobby(room_code, username):
        session['username'] = username
        session['room'] = room_code
        return redirect(url_for('waiting_room', room_code=room_code))
    else:
        return "Lobby tidak ditemukan atau penuh.", 404

@app.route('/waiting/<room_code>')
def waiting_room(room_code):
    return render_template('waiting_room.html', room_code=room_code)

@app.route('/lobby/<room_code>')
def lobby(room_code):
    # Ambil soal pertama
    question = game_state.get_current_question(room_code)
    return render_template('lobby.html', room_code=room_code, question=question)
    
@socketio.on('join')
def on_join(data):
    room = data['room']
    username = data['username']
    join_room(room)
    emit('player_joined', {'players': lobbies.get_players(room)}, room=room)
    game_state.sid_to_username[request.sid] = username

@socketio.on('enter_lobby')
def on_enter_lobby(data):
    room = data['room']
    question = game_state.get_current_question(room)
    emit('start_question', {'question': question}, room=request.sid)

@socketio.on('start_game')
def on_start(data):
    room = data['room']
    game_state.start_game(room, lobbies.get_players(room))
    question = game_state.get_current_question(room)
    emit('game_started', {'room': room}, room=room)

@socketio.on('submit_code')
def handle_code_submission(data):
    room = data['room']
    username = game_state.sid_to_username.get(request.sid)
    code = data['code']
    emit('code_result', {'username': username, 'correct': False}, room=request.sid)
    result = game_state.evaluate_code(room, code)

    if result['correct']:
        game_state.increment_score(room, username)
        if game_state.next_question(room):
            next_q = game_state.get_current_question(room)
            emit('correct_answer', {'username': username, 'question': next_q}, room=room)
        else:
            winner = game_state.get_winner(room)
            emit('game_over', {'winner': winner, 'scores': game_state.get_scores(room)}, room=room)
    else:
        emit('code_result', {'username': username, 'correct': False}, room=request.sid)

if __name__ == '__main__':
    socketio.run(app, debug=True)