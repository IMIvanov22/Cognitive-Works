from flask import Flask, render_template, request, jsonify
from DB.database import Database

app = Flask(__name__)
db = Database(app, wipeDB= True, backend='sqlite')

@app.route('/')
def home():
    return render_template('home.html')
@app.route('/login')
def login():
    return render_template('login.html')
@app.route('/register')
def register():
    return render_template('register.html')
@app.route('/history')
def history():
    return render_template('history.html')

@app.route('/api/signup', methods=['POST'])
def api_register():
    username = request.form.get('username')
    password = request.form.get('password')
    print(username, password)

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400


    return jsonify({"message": "account created successfully"}), 200

@app.route('/api/login', methods=['POST'])
def api_login():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400


    token = "example_token"

    return jsonify({"token": token}), 200

@app.route('/api/self', methods=['POST'])
def api_self():
    token = request.headers.get('token')

    if not token:
        return jsonify(), 401


    username = "example_user"

    return jsonify({"username": username}), 200

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    token = request.headers.get('token')
    image = request.files.get('image')

    if not token:
        return jsonify({"error": "Missing token"}), 401

    if not image:
        return jsonify({"error": "No image uploaded"}), 400



    analysis_id = "12345"

    return jsonify({"id": analysis_id}), 200

@app.route('/api/history', methods=['POST'])
def api_history():
    token = request.headers.get('token')

    if not token:
        return jsonify({"error": "Missing token"}), 401

    history = [
        {"id": "12345", "result": "example"}
    ]

    return jsonify({"history": history}), 200

if __name__ == '__main__':
    app.run()
