import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import secrets
from firebase import firebase

# Generate a secret key if not provided in the environment
SECRET_KEY = os.environ.get('SECRET_KEY', secrets.token_hex(16))

app = Flask(__name__)
firebase = firebase.FirebaseApplication('https://telebar-a-default-rtdb.europe-west1.firebasedatabase.app/', None)
app.secret_key = SECRET_KEY

# In-memory storage for chat messages
chat_history = []

@app.route('/')
def home():
    # Redirect to login if not signed in
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('chat.html', username=session['username'], password=session['password'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if username:
            if password:
                session['username'] = username
                session['password'] = password
                return redirect("/verify")
            return render_template('login.html', error="Password cannot be empty")
        return render_template('login.html', error="Username cannot be empty.")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('password', None)
    return redirect(url_for('login'))

@app.route('/send_message', methods=['POST'])
def send_message():
    if 'username' not in session or 'password' not in session:
        return jsonify({'status': 'error', 'message': 'User not logged in'}), 403

    data = request.json
    message = data.get('message', '').strip()
    if message:
        chat_history.append({'username': session['username'], 'message': message})
        return jsonify({'status': 'success', 'history': chat_history})
    return jsonify({'status': 'error', 'message': 'No message provided'}), 400

@app.route('/get_messages', methods=['GET'])
def get_messages():
    return jsonify({'history': chat_history})

@app.route('/hack', methods=['GET'])
def hacker():
    return render_template('hack.html')

@app.route('/verify', methods=['GET'])
def authenticate():
    try:
        result = firebase.get('/user', session['username'].lower())
        if str(result) == session['password']:
            return redirect(url_for('home'))
        return render_template('login.html', error="Password or user incorrect")
    except:
        return render_template('login.html', error="User or password incorrect")

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=3)
