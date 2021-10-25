from hashlib import new
from os import name

from flask.helpers import flash
from flaskChat.models import User
from flask_socketio import SocketIO, send, emit, join_room
from flaskChat import app, socketio, db, bcrypt, mail
from flask import render_template, redirect, request, url_for
from flaskChat.forms import LoginForm, RegisterForm, ResetPasswordForm, ResetRequestForm
from flaskChat.models import Messages
from flask_login import login_user, login_required, current_user, logout_user
from flask_mail import Message


# Index page will return the chat options
@app.route("/")
@login_required
def index():
    return render_template('index.html')


# Login page
@app.route("/login", methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect("/")
    form = LoginForm()
    next_page = request.args.get('next')
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect(next_page) if next_page else redirect("/")
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', form=form)


# logout Page
@app.route("/logout")
def logout():
    logout_user()
    return redirect("/login")


# Register Page
@app.route("/register", methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect("/")
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        return redirect("/login")
    return render_template('register.html', form=form)


# Function for sending the token to the email of the user for resetting the password 
def sendMail(user):
    token = user.generate_token()
    msg = Message('Password Reset Request', sender='noreply@demo.com', recipients=[user.email])
    msg.body = f""" To reset your password, visit the following link:
    {url_for('reset_password', token=token, _external=True)}
    If you did not make this request then simply ignore this email and no change will be made."""
    mail.send(msg)


# Request reset password page
@app.route("/reset_request", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect("/")
    form = ResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        sendMail(user)
        return redirect("/login")
    return render_template('reset_request.html', form=form)


# Page for resetting the password
@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_password(token):
    user = User.check_token(token)
    if not user:
        return redirect("/reset_request")
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        return redirect("/login")
    return render_template('reset_password.html', form=form)


# Inbox page
@app.route("/chat/private")
@login_required
def inbox():
    return render_template("inbox.html")


# Global chat page
@app.route("/chat/global")
@login_required
def global_chat():
    messages = Messages.query.filter_by(chat='global').all()
    return render_template("global.html", messages=messages)


# Connected to global page websocket
@socketio.on('userConnected-global', namespace='/chat/global')
def joined_globalChat():
    msg = current_user.username
    emit('joined-global', msg, broadcast=True)


# Global page messages handler
@socketio.on('sendMessage', namespace='/chat/global')
def global_messages(msg):
    message = msg['message']
    data = {
        'Message': message,
            'User': current_user.username
        }
    message = Messages(message=msg['message'], user_id=current_user.id, chat='global')
    db.session.add(message)
    db.session.commit()
    emit('userMessage', data, broadcast=True)


# User disconnected the global chat
@socketio.on('disconnect', namespace='/chat/global')
def disconnected_global():
    emit('userDisconnected', current_user.username, broadcast=True)


# Anime Chat Page
@app.route("/chat/anime")
@login_required
def anime_chat():
    messages = Messages.query.filter_by(chat='anime').all()
    return render_template('animeChat.html', messages=messages)


#Listening to the event of the user being connected and emitting a message with username of the user
@socketio.on('userConnected-anime', namespace='/chat/anime')
def joined_animeChat():
    join_room('anime')
    emit('joined-anime', current_user.username, to='anime')


# Handlinng the messages sent by the user
@socketio.on('sendMessage', namespace='/chat/anime')
def anime_messages(msg):
    data = {
        'Message': msg,
        'User': current_user.username,
    }
    messages = Messages(message=msg, user_id=current_user.id, chat='anime')
    db.session.add(messages)
    db.session.commit()
    emit('userMessage', data, to='anime')
    

# Informing the client username that disconnected from the room
@socketio.on('disconnect', namespace='/chat/anime')
def disconnected_anime():
    emit('userDisconnected', current_user.username, to='anime')


# Rendering the movies chat page
@app.route('/chat/movies')
def movies_chat():
    messages = Messages.query.filter_by(chat='movies').all()
    return render_template('moviesChat.html', messages=messages)


#Listening to the event of the user being connected and emitting a message with username of the user
@socketio.on('userConnected-movies', namespace='/chat/movies')
def joined_moviesChat():
    join_room('movies')
    emit('joined-movies', current_user.username, to='movies')


# Handlinng the messages sent by the user
@socketio.on('sendMessage', namespace='/chat/movies')
def movies_messages(msg):
    data = {
        'user': current_user.username,
        'message': msg
    }
    message = Messages(message=msg, user_id=current_user.id, chat='movies')
    db.session.add(message)
    db.session.commit()
    emit('userMessage', data, to='movies')


# Informing the client username that disconnected from the room
@socketio.on('disconnect', namespace='/chat/movies')
def disconnected_movies():
    emit('userDisconnected', current_user.username, to='movies')


# Rendering the books chat page
@app.route('/chat/books')
def books_chat():
    messages = Messages.query.filter_by(chat='books').all()
    return render_template('booksChat.html', messages=messages)


#Listening to the event of the user being connected and emitting a message with username of the user
@socketio.on('userConnected-books', namespace='/chat/books')
def joined_booksChat():
    join_room('books')
    emit('joined-books', current_user.username, to='books')


# Handlinng the messages sent by the user
@socketio.on('sendMessage', namespace='/chat/books')
def books_messages(msg):
    data = {
        'user': current_user.username,
        'message': msg
    }
    message = Messages(message=msg, user_id=current_user.id, chat='books')
    db.session.add(message)
    db.session.commit()
    emit('userMessage', data, to='books')


# Informing the client username that disconnected from the room
@socketio.on('disconnect', namespace='/chat/books')
def disconnected_books():
    emit('userDisconnected', current_user.username, to='books')


# Rendering the game chat page
@app.route('/chat/games')
def games_chat():
    messages = Messages.query.filter_by(chat='games').all()
    return render_template('gamesChat.html', messages=messages)


#Listening to the event of the user being connected and emitting a message with username of the user
@socketio.on('userConnected-games', namespace='/chat/games')
def joined_gamesChat():
    join_room('games')
    emit('joined-games', current_user.username, to='games')


# Handlinng the messages sent by the user
@socketio.on('sendMessage', namespace='/chat/games')
def games_messages(msg):
    data = {
        'user': current_user.username,
        'message': msg
    }
    message = Messages(message=msg, user_id=current_user.id, chat='games')
    db.session.add(message)
    db.session.commit()
    emit('userMessage', data, to='games')


# Informing the client username that disconnected from the room
@socketio.on('disconnect', namespace='/chat/games')
def disconnected_games():
    emit('userDisconnected', current_user.username, to='games')