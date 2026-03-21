import csv
import os
from flask import Flask, render_template, request, jsonify
from DB.database import Database
from AI.face_predictor import FacePredictor
from PIL import Image

app = Flask(__name__)
app.secret_key = 'skincare-secret-key'
db = Database(app, wipeDB= False, backend='sqlite')

predictor = None
def get_predictor():
    global predictor
    if predictor is None:
        predictor = FacePredictor()
    return predictor

def load_skincare_products():
    products = []
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'skincare.csv')
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if None in row or not row.get('age_group', '').strip().isdigit():
                continue
            products.append({
                'product_name': row['product_name'],
                'brand': row['brand'],
                'good_for_acne': int(row['good_for_acne']),
                'gender': row['gender'].strip().lower(),
                'age_group': int(row['age_group']),
            })
    return products

skincare_products = load_skincare_products()

def get_recommendations(predictions, limit=10):
    gender = predictions['gender'].lower()
    age_group = predictions['age_group_id']
    high_acne = predictions['acne_severity_id'] == 1

    matched = []
    for p in skincare_products:
        if p['gender'] != gender:
            continue
        if p['age_group'] != age_group:
            continue
        if high_acne and not p['good_for_acne']:
            continue
        matched.append({
            'product_name': p['product_name'],
            'brand': p['brand'],
            'good_for_acne': bool(p['good_for_acne']),
        })
        if len(matched) >= limit:
            break
    return matched

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

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    if db.user_exists(username):
        return jsonify({"error": "Username already taken"}), 409

    db.create_user(username, password)

    return jsonify({"message": "account created successfully"}), 200

@app.route('/api/login', methods=['POST'])
def api_login():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    if not db.user_exists(username):
        return jsonify({"error": "Invalid credentials"}), 401

    if not db.verify_user(username, password):
        return jsonify({"error": "Invalid credentials"}), 401

    token = db.create_token(username)

    return jsonify({"token": token}), 200

@app.route('/api/self', methods=['POST'])
def api_self():
    token = request.headers.get('token')

    if not token:
        return jsonify(), 401

    username = db.get_user(token)

    if not username:
        return jsonify(), 401

    return jsonify({"username": username}), 200

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    token = request.headers.get('token')
    image = request.files.get('image')

    if not token:
        return jsonify({"error": "Missing token"}), 401

    username = db.get_user(token)
    if not username:
        return jsonify({"error": "Invalid token"}), 401

    if not image:
        return jsonify({"error": "No image uploaded"}), 400

    try:
        img = Image.open(image.stream).convert("RGB")
        fp = get_predictor()
        predictions = fp.predict(img)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    recommendations = get_recommendations(predictions)

    db.create_analysis(username, predictions["age_group_id"], recommendations)

    return jsonify({"predictions": predictions, "recommendations": recommendations}), 200

@app.route('/api/history', methods=['POST'])
def api_history():
    token = request.headers.get('token')

    if not token:
        return jsonify({"error": "Missing token"}), 401

    username = db.get_user(token)
    if not username:
        return jsonify({"error": "Invalid token"}), 401

    analyses = db.get_analyses(username)

    return jsonify({"history": analyses}), 200

@app.route('/api/logout', methods=['POST'])
def api_logout():
    token = request.headers.get('token')

    if not token:
        return jsonify({"error": "Missing token"}), 401

    username = db.get_user(token)
    if not username:
        return jsonify({"error": "Invalid token"}), 401

    db.delete_tokens(username)

    return jsonify({"message": "logged out"}), 200

if __name__ == '__main__':
    app.run()
