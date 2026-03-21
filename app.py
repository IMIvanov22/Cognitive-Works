import csv
import os
from flask import Flask, render_template, request, jsonify
from DB.database import Database
from AI.face_predictor import FacePredictor, SKIN_LABELS
from PIL import Image
import numpy as np

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
            good_for_cols = [k for k in row.keys() if isinstance(k, str) and k.startswith('good_for_')]
            products.append({
                'product_name': row['product_name'],
                'brand': row['brand'],
                'gender': row['gender'].strip().lower(),
                'age_group': int(row['age_group']),
                'good_for': {k: bool(int(row.get(k, '0') or '0')) for k in good_for_cols},
            })
    return products

skincare_products = load_skincare_products()

_CONDITION_TO_PRODUCT_COL = {
    "acne": "good_for_acne",
    "redness": "good_for_redness",
    "pigmentation": "good_for_pigmentation",
    "wrinkles": "good_for_wrinkles",
}

def _normalize_gender(gender):
    if not gender:
        return None
    g = str(gender).strip().lower()
    if g in {"m", "man", "male"}:
        return "male"
    if g in {"f", "woman", "female"}:
        return "female"
    if g in {"unisex", "any", "all"}:
        return "unisex"
    return g

def _map_age_group_to_dataset(age_group_id):
    if age_group_id is None:
        return None
    try:
        n = int(age_group_id)
    except Exception:
        return None
    if n in (0, 1, 2):
        return n + 1
    if n in (1, 2, 3):
        return n
    return None

def select_skin_conditions(probs, *, threshold=0.5):
    probs = np.asarray(probs, dtype=np.float32).reshape(-1)

    picked = [SKIN_LABELS[i] for i, p in enumerate(probs) if float(p) >= threshold]
    if not picked:
        picked = [SKIN_LABELS[int(np.argmax(probs))]]

    if "normal_skin" in picked:
        return ["normal_skin"]
    return picked

def get_recommendations(
    *,
    picked_conditions,
    demographics=None,
    limit=10,
):
    normal_only = picked_conditions == ["normal_skin"]

    gender = None
    age_group = None
    if demographics:
        gender = _normalize_gender(demographics.get("gender", None))
        age_group = _map_age_group_to_dataset(demographics.get("age_group_id", None))

    wanted_conditions = [c for c in picked_conditions if c != "normal_skin"]

    def product_match_score(prod):
        good_for = prod.get("good_for", {}) or {}
        score = 0
        for cond in wanted_conditions:
            col = _CONDITION_TO_PRODUCT_COL.get(cond)
            if not col:
                continue
            if bool(good_for.get(col, False)):
                score += 1
        return score

    def build_candidates(*, ignore_gender, ignore_age, allow_nonmatching):
        out = []
        for p in skincare_products:
            p_gender = str(p.get("gender", "")).strip().lower()
            if not ignore_gender and gender is not None:
                if p_gender not in {"unisex", gender}:
                    continue

            if not ignore_age and age_group is not None and int(p.get("age_group", -1)) != age_group:
                continue

            if normal_only:
                good_for = p.get("good_for", {}) or {}
                if any(bool(v) for v in good_for.values()):
                    continue
                score = 0
            else:
                score = product_match_score(p)
                if wanted_conditions and score <= 0 and not allow_nonmatching:
                    continue

            out.append((score, p))
        out.sort(
            key=lambda t: (
                -t[0],
                str(t[1].get("brand", "")).lower(),
                str(t[1].get("product_name", "")).lower(),
            )
        )
        return out

    candidates = build_candidates(ignore_gender=False, ignore_age=False, allow_nonmatching=False)
    if not candidates and gender is not None:
        candidates = build_candidates(ignore_gender=True, ignore_age=False, allow_nonmatching=False)
    if not candidates and age_group is not None:
        candidates = build_candidates(ignore_gender=False, ignore_age=True, allow_nonmatching=False)
    if not candidates and (gender is not None or age_group is not None):
        candidates = build_candidates(ignore_gender=True, ignore_age=True, allow_nonmatching=False)
    if not candidates and wanted_conditions and not normal_only:
        candidates = build_candidates(ignore_gender=True, ignore_age=True, allow_nonmatching=True)

    matched = []
    for _, p in candidates[:limit]:
        good_for = p.get("good_for", {}) or {}
        matched.append(
            {
                "product_name": p.get("product_name"),
                "brand": p.get("brand"),
                "good_for_acne": bool(good_for.get("good_for_acne", False)),
                "good_for_redness": bool(good_for.get("good_for_redness", False)),
                "good_for_pigmentation": bool(good_for.get("good_for_pigmentation", False)),
                "good_for_wrinkles": bool(good_for.get("good_for_wrinkles", False)),
            }
        )
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
        probs = fp.predict(img)
        picked = select_skin_conditions(probs, threshold=0.5)
        try:
            demographics = fp.predict_demographics(img)
        except Exception:
            demographics = None
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    recommendations = get_recommendations(picked_conditions=picked, demographics=demographics)

    skin_type_id = int(np.argmax(np.asarray(probs, dtype=np.float32)))
    db.create_analysis(username, skin_type_id, recommendations)

    predictions_payload = {"picked": picked}
    if demographics:
        predictions_payload.update(demographics)

    return jsonify({"predictions": predictions_payload, "recommendations": recommendations}), 200

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