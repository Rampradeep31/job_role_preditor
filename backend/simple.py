import pickle
import json
import os
import pandas as pd
import numpy as np
import warnings
from datetime import timedelta, datetime
from functools import wraps

# Flask & Auth
from flask import Flask, jsonify, request
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Education, PredictionHistory

# Google Auth
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

# Machine Learning
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import MinMaxScaler

# 🔇 SILENCE TERMINAL WARNINGS
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

# =========================================================
# ⚙️ CONFIGURATION
# =========================================================
GOOGLE_CLIENT_ID = "983358026198-c1vfs6d2eclv3lfu4a3rdg6u3q3c72sk.apps.googleusercontent.com"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "database")
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "users.db")
MODEL_DIR = os.path.join(BASE_DIR, "database", "ml", "models")
os.makedirs(MODEL_DIR, exist_ok=True)
UPLOAD_FOLDER = os.path.join(BASE_DIR, "database", "datasets")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -----------------------------------------------------------
# DATABASE INIT
# -----------------------------------------------------------
engine = create_engine(f"sqlite:///{os.path.abspath(DB_PATH)}", connect_args={"check_same_thread": False})
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# -----------------------------------------------------------
# FLASK APP SETUP
# -----------------------------------------------------------
app = Flask(__name__)
CORS(app) 
app.config["JWT_SECRET_KEY"] = "super-secret-key" 
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
jwt = JWTManager(app)

# -----------------------------------------------------------
# GLOBAL ML VARIABLES
# -----------------------------------------------------------
le_degree, le_field, scaler, le_target, model = None, None, None, None, None
KEY_SKILLS = ['python', 'java', 'aws', 'react', 'cpa', 'autocad', 'scrum', 'six sigma']

# 🟢 MASTER CURRICULUM MAP (The Source of Truth)
# The backend will STRICTLY enforce these relationships.
MASTER_CURRICULUM = {
    "CS & IT": {
        "degrees": ["Computer Science Engineering", "Information Technology", "AI & Machine Learning", "AI & Data Science", "Cybersecurity", "Data Science", "Computer Science", "IT"],
        "roles": ["AI Engineer", "Data Scientist", "Full Stack Developer", "Software Engineer", "Backend Developer", "Frontend Developer", "Cybersecurity Analyst", "System Engineer"]
    },
    "Electronics": {
        "degrees": ["Electronics & Communication Engineering", "Electrical & Electronics Engineering", "Electrical Engineering", "Instrumentation Engineering", "Electronics"],
        "roles": ["VLSI Design Engineer", "Embedded Systems Engineer", "Control Systems Engineer", "Network Engineer", "Maintenance Engineer"]
    },
    "Core Engineering": {
        "degrees": ["Mechanical Engineering", "Civil Engineering", "Chemical Engineering", "Production Engineering", "Metallurgical Engineering", "Mining Engineering"],
        "roles": ["Project Manager", "Structural Engineer", "Process Engineer", "Mechanical Design Engineer", "Site Supervisor"]
    },
    "Specialized Engineering": {
        "degrees": ["Robotics & Automation", "Biotechnology", "Biomedical Engineering", "Aerospace Engineering", "Aeronautical Engineering", "Automobile Engineering", "Mechatronics Engineering", "Marine Engineering", "Petroleum Engineering", "Food Technology", "Textile Engineering", "Environmental Engineering", "Agriculture Engineering"],
        "roles": ["Robotics Engineer", "Biomedical Engineer", "Automotive Design Engineer", "Marine Engineer", "Food Safety Officer"]
    },
    "Management (UG)": {
        "degrees": ["Finance", "Marketing", "Human Resource Management", "Business Analytics", "International Business", "Logistics & Supply Chain", "Operations Management", "Entrepreneurship", "Digital Marketing"],
        "roles": ["Business Analyst", "Marketing Executive", "HR Generalist", "Operations Coordinator", "Sales Manager"]
    },
    "Service Sector": {
        "degrees": ["Hospitality Management", "Travel & Tourism", "Retail Management", "Banking & Insurance", "Aviation Management", "Healthcare Management"],
        "roles": ["Hotel Manager", "Retail Store Manager", "Aviation Operations Manager", "Hospital Administrator", "Relationship Manager"]
    },
    "Management (PG)": {
        "degrees": ["Finance (Advanced)", "Marketing (Advanced)", "Human Resource (Advanced)", "Business Analytics (Advanced)", "International Business (Advanced)", "Operations Management (Advanced)", "IT Management", "Entrepreneurship (Advanced)", "Digital Marketing (Advanced)"],
        "roles": ["Investment Banker", "Product Manager", "HR Director", "Management Consultant", "Business Development Manager"]
    },
    "Specialized Management": {
        "degrees": ["Logistics & Supply Chain (Advanced)", "Hospitality & Tourism (Advanced)", "Healthcare Management (Advanced)", "Retail Management (Advanced)", "Banking & Financial Services", "Agri-Business Management", "Aviation Management (Advanced)"],
        "roles": ["Supply Chain Manager", "Hospital Administrator", "Portfolio Manager", "Retail Operations Head", "Agri-Business Manager"]
    },
    "Design": {
        "degrees": ["Fashion Design", "Interior Design", "Product Design", "Communication Design", "Graphic Design", "UI/UX Design", "Industrial Design", "Animation & Multimedia", "Game Design", "Textile Design", "Jewellery Design"],
        "roles": ["UI/UX Designer", "Product Designer", "Fashion Stylist", "Game Artist", "Interior Architect"]
    },
    "Humanities": {
        "degrees": ["English", "Psychology", "Sociology", "Economics", "Political Science", "History", "Geography", "Philosophy", "Education", "Hindi", "Tamil", "Sanskrit"],
        "roles": ["Content Writer", "Psychologist", "Policy Analyst", "Teacher", "Social Worker"]
    },
    "Creative Arts": {
        "degrees": ["Journalism & Mass Communication", "Public Administration", "Fine Arts", "Performing Arts"],
        "roles": ["Journalist", "Public Relations Officer", "Art Director", "Civil Servant", "Media Planner"]
    },
    "Commerce": {
        "degrees": ["Accounting & Finance", "Banking & Insurance", "Taxation", "Auditing", "Computer Applications", "Business Analytics", "Economics", "Financial Markets", "International Business", "Corporate Secretaryship"],
        "roles": ["Chartered Accountant", "Financial Auditor", "Tax Consultant", "Investment Analyst", "Bank Officer"]
    },
    "Tech & Science": {
        "degrees": ["Computer Science", "Information Technology", "Data Science", "Artificial Intelligence", "Mathematics", "Physics", "Chemistry", "Electronics", "Statistics", "Forensic Science"],
        "roles": ["Software Developer", "Lab Technician", "Data Analyst", "Research Assistant", "Forensic Expert"]
    },
    "Life Sciences": {
        "degrees": ["Biotechnology", "Microbiology", "Agriculture", "Environmental Science", "Psychology", "Nutrition & Dietetics", "Fashion Design", "Nursing"],
        "roles": ["Clinical Research Associate", "Microbiologist", "Dietician", "Agricultural Officer", "Registered Nurse"]
    },
    "Masters Engineering": {
        "degrees": ["Computer Science Engineering (Masters)", "Information Technology (Masters)", "Data Science (Masters)", "Artificial Intelligence (Masters)", "Machine Learning", "Cybersecurity (Masters)", "VLSI", "Embedded Systems", "Power Systems", "Thermal Engineering", "Structural Engineering", "Robotics", "Biotechnology (Masters)", "Environmental Engineering (Masters)", "Mechanical Design", "Manufacturing Engineering", "Transportation Engineering"],
        "roles": ["R&D Engineer", "Senior Data Scientist", "VLSI Architect", "Structural Consultant", "Robotics System Architect"]
    },
    "Masters Science": {
        "degrees": ["Computer Science (M.Sc)", "Information Technology (M.Sc)", "Mathematics (M.Sc)", "Physics (M.Sc)", "Chemistry (M.Sc)", "Electronics (M.Sc)", "Data Science (M.Sc)", "Artificial Intelligence (M.Sc)", "Statistics (M.Sc)", "Biotechnology (M.Sc)", "Microbiology (M.Sc)", "Agriculture (M.Sc)", "Environmental Science (M.Sc)", "Psychology (M.Sc)", "Food Science & Nutrition", "Forensic Science (M.Sc)"],
        "roles": ["Senior Researcher", "Data Engineer", "Clinical Psychologist", "Food Scientist", "Statistician"]
    }
}

def load_models():
    global le_degree, le_field, scaler, le_target, model
    try:
        with open(os.path.join(MODEL_DIR, "degree_encoder.pkl"), "rb") as f: le_degree = pickle.load(f)
        with open(os.path.join(MODEL_DIR, "field_encoder.pkl"), "rb") as f: le_field = pickle.load(f)
        with open(os.path.join(MODEL_DIR, "scaler.pkl"), "rb") as f: scaler = pickle.load(f)
        with open(os.path.join(MODEL_DIR, "target_encoder.pkl"), "rb") as f: le_target = pickle.load(f)
        with open(os.path.join(MODEL_DIR, "model.pkl"), "rb") as f: model = pickle.load(f)
        print("✅ Models Loaded Successfully!")
        return True
    except Exception as e:
        print("⚠️ Warning: Models not found.", e)
        return False

load_models()

# -----------------------------------------------------------
# ADMIN DECORATOR
# -----------------------------------------------------------
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_username = get_jwt_identity()
        session = Session()
        try:
            user = session.query(User).filter_by(username=current_username).first()
            if not user or user.role != 'admin': return jsonify({"error": "Admin access required"}), 403
        finally:
            session.close()
        return f(*args, **kwargs)
    return decorated_function

# -----------------------------------------------------------
# 🚀 PREDICT ROUTE (STRICT WHITELIST FILTERING)
# -----------------------------------------------------------
@app.route("/predict", methods=["POST"])
@jwt_required()
def predict_role():
    session = Session()
    try:
        if not model: return jsonify({"error": "Model not ready."}), 503
        username = get_jwt_identity()
        user = session.query(User).filter_by(username=username).first()
        if not user: return jsonify({"error": "User not found"}), 404

        data = request.get_json()

        # 1. ENCODE INPUTS
        degree_input = data.get("Degree", "").strip()
        encoded_degree = 0
        if le_degree:
            if degree_input in le_degree.classes_:
                encoded_degree = int(le_degree.transform([degree_input])[0])
            elif "Other" in le_degree.classes_:
                encoded_degree = int(le_degree.transform(["Other"])[0])

        spec_input = data.get("Field_of_Study", "").strip()
        final_field = spec_input if spec_input in le_field.classes_ else ("Other" if "Other" in le_field.classes_ else spec_input)
        encoded_spec = int(le_field.transform([final_field])[0]) if final_field in le_field.classes_ else 0

        # FIX: Remove Warning using DataFrame
        gpa_input = float(data.get("University_GPA", 0))
        gpa_scaled = 0.0
        if scaler:
            gpa_df = pd.DataFrame([[gpa_input]], columns=['University_GPA'])
            gpa_scaled = float(scaler.transform(gpa_df)[0][0])
        else:
            gpa_scaled = gpa_input

        cert_input = str(data.get("Certifications", "")).lower()
        cert_count = len(cert_input.split(',')) if cert_input and cert_input != "none" else 0
        intern_val = int(data.get("Internships_Completed", 0))

        skill_flags = [1 if s in cert_input else 0 for s in KEY_SKILLS]

        # 2. PREDICT RAW PROBABILITIES
        input_vector = [encoded_degree, encoded_spec, gpa_scaled, cert_count, intern_val] + skill_flags
        probs = model.predict_proba([input_vector])[0]
        classes = le_target.classes_ 
        
        # 🟢 3. STRICT DOMAIN ENFORCEMENT (The Fix)
        # Find which "Bucket" the user belongs to based on Field of Study
        allowed_roles = []
        user_category = None
        
        # Search the MASTER_CURRICULUM for the user's field
        search_str = spec_input.lower()
        
        for category, info in MASTER_CURRICULUM.items():
            # Check if user's field matches any degree in this category
            # We use substring match to catch "Information Technology" inside "B.Tech Information Technology"
            for d in info['degrees']:
                if d.lower() == search_str or d.lower() in search_str or search_str in d.lower():
                    allowed_roles = info['roles']
                    user_category = category
                    break
            if allowed_roles:
                break
        
        # 🟢 4. HARD FILTERING
        top_indices = []
        
        if allowed_roles:
            # Filter: Find indices of roles that are in the Allowed List
            valid_indices = []
            for i, role_name in enumerate(classes):
                if role_name in allowed_roles:
                    valid_indices.append(i)
            
            # If we found matches in the model's classes
            if valid_indices:
                # Extract probs for ONLY valid roles
                valid_probs = probs[valid_indices]
                
                # Sort these valid roles by probability
                sorted_local_idx = np.argsort(valid_probs)[-5:][::-1]
                
                # Map back to original indices
                top_indices = [valid_indices[i] for i in sorted_local_idx]
            else:
                # Fallback: If map has roles but model doesn't know them (rare), use raw
                top_indices = np.argsort(probs)[-5:][::-1]
        else:
            # Fallback: No category found, use raw ML predictions
            top_indices = np.argsort(probs)[-5:][::-1]

                # 5. FORMAT RESULTS
        all_recommendations = []

        raw_scores = [max(probs[i], 0) for i in top_indices]
        total_score = sum(raw_scores) if sum(raw_scores) > 0 else 1.0

        for i, idx in enumerate(top_indices):
            role = classes[idx]
            raw_prob = probs[idx]

            # 🔹 Confidence smoothing (UI-safe)
            rank = i + 1
            base_conf = (raw_prob / total_score) * 100 if total_score > 0 else 0

            if rank == 1:
                boosted_conf = min(85, max(base_conf, 60))
            elif rank == 2:
                boosted_conf = min(59, max(base_conf, 30))
            elif rank == 3:
                boosted_conf = min(30, max(base_conf, 25))
            else:
                boosted_conf = min(25, max(base_conf, 3))

            all_recommendations.append({
                "role": role,
                "confidence": f"{boosted_conf:.1f}%"
            })

        top_match = all_recommendations[0] if all_recommendations else None
        alternates = all_recommendations[1:] if len(all_recommendations) > 1 else []


        # 6. SAVE HISTORY
        history_id = None
        if top_match:
            hist = PredictionHistory(
                user_id=user.id, top_role=top_match["role"],
                confidence=top_match["confidence"],
                all_recommendations=str([r["role"] for r in all_recommendations]),
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            session.add(hist)
            session.commit()
            history_id = hist.id 

        return jsonify({
            "status": "success", 
            "history_id": history_id, 
            "top_match": top_match,   
            "alternates": alternates, 
            "recommendations": all_recommendations,
            "used_field": final_field,
            "detected_category": user_category # Helpful for debugging
        }), 200
    except Exception as e:
        print("Prediction Error:", e)
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

# -----------------------------------------------------------
# HISTORY ROUTE
# -----------------------------------------------------------
@app.route("/history", methods=["GET"])
@jwt_required()
def get_history():
    session = Session()
    try:
        username = get_jwt_identity()
        user = session.query(User).filter_by(username=username).first()
        if not user: return jsonify({"error": "User not found"}), 404

        history = session.query(PredictionHistory).filter_by(user_id=user.id).order_by(PredictionHistory.id.desc()).limit(10).all()
        if not history: return jsonify([]), 200

        return jsonify([{
            "role": h.top_role, "confidence": h.confidence, "date": h.timestamp
        } for h in history]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

# -----------------------------------------------------------
# AUTH ROUTES
# -----------------------------------------------------------
@app.route("/signup", methods=["POST"])
def signup():
    session = Session()
    try:
        data = request.get_json() or {}
        username, email, password = data.get("username"), data.get("email"), data.get("password")
        if session.query(User).filter_by(email=email).first(): return jsonify({"error": "Email exists"}), 409
        user = User(username=username, email=email, password=password, role="student")
        session.add(user)
        session.commit()
        return jsonify({"message": "Signup successful"}), 201
    except Exception as e: return jsonify({"error": str(e)}), 500
    finally: session.close()

@app.route("/login", methods=["POST"])
def login():
    session = Session()
    try:
        data = request.get_json() or {}

        login_input = data.get("email") or data.get("username")
        password = data.get("password")

        # ✅ Allow login via username OR email
        user = session.query(User).filter(
            (User.email == login_input) | (User.username == login_input)
        ).first()

        if not user or user.password != password:
            return jsonify({"error": "Invalid credentials"}), 401

        token = create_access_token(identity=user.username)

        return jsonify({
            "message": "Login successful",
            "token": token,
            "role": user.role   # 🔥 REQUIRED for admin redirect
        }), 200

    finally:
        session.close()


@app.route("/google-login", methods=["POST"])
def google_login():
    session = Session()
    try:
        data = request.get_json() or {}
        token = data.get("token")
        try:
            idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), audience=GOOGLE_CLIENT_ID)
        except ValueError:
             return jsonify({"error": "Invalid Google Token"}), 400

        email = idinfo.get("email")
        if not email: return jsonify({"error": "Invalid Google account"}), 400

        user = session.query(User).filter_by(email=email).first()
        if not user:
            user = User(username=email.split("@")[0], email=email, password="", role="student")
            session.add(user)
            session.commit()

        jwt_token = create_access_token(identity=user.username)
        return jsonify({"message": "Google Login Successful", "token": jwt_token, "role": user.role}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()

# -----------------------------------------------------------
# PROFILE & OTHER ROUTES
# -----------------------------------------------------------
# -----------------------------------------------------------
# PROFILE
# -----------------------------------------------------------
@app.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    session = Session()
    try:
        username = get_jwt_identity()
        user = session.query(User).filter_by(username=username).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        edu = session.query(Education).filter_by(user_id=user.id).first()

        return jsonify({
            # BASIC INFO
            "username": user.username,
            "email": user.email,
            "phone": user.phone or "--",

            # SKILLS & INTERNSHIP (FROM USER TABLE)
            "skills": user.skills or "Not set",
            "internship": user.internship or "No",
            "duration": user.duration or "--",

            # EDUCATION (FROM EDUCATION TABLE)
            "degree": edu.degree if edu else "--",
            "specialization": edu.specialization if edu else "--",
            "cgpa": edu.cgpa if edu else "--",
            "year": edu.year_of_graduation if edu else "--",
            "university": edu.university if edu else "--",
            "certifications": edu.certifications if edu else "--"
        }), 200

    finally:
        session.close()

# -----------------------------------------------------------
# UPDATE PROFILE ROUTE (Fixed to save ALL fields)
# -----------------------------------------------------------
@app.route("/profile/update", methods=["PATCH"])
@jwt_required()
def update_profile():
    session = Session()
    try:
        username = get_jwt_identity()
        user = session.query(User).filter_by(username=username).first()
        if not user: return jsonify({"error": "User not found"}), 404

        data = request.get_json()

        # 1. Update USER fields
        if "phone" in data: user.phone = data["phone"]
        if "skills" in data: user.skills = data["skills"]
        if "internship" in data: user.internship = data["internship"] # Yes/No
        if "duration" in data: user.duration = data["duration"]       # e.g., "3 Months"
        if "preferred_role" in data: user.preferred_role = data["preferred_role"]

        # 2. Update EDUCATION fields
        edu = session.query(Education).filter_by(user_id=user.id).first()
        if not edu: 
            edu = Education(user_id=user.id)
            session.add(edu)
            
        if "degree" in data: edu.degree = data["degree"]
        if "specialization" in data: edu.specialization = data["specialization"]
        if "cgpa" in data: edu.cgpa = float(data["cgpa"])
        if "certifications" in data: edu.certifications = data["certifications"]
        if "university" in data: edu.university = data["university"]
        if "year" in data: edu.year_of_graduation = data["year"] # Matches "gradYear" from frontend

        session.commit()
        return jsonify({"message": "Profile updated successfully"}), 200
    except Exception as e:
        session.rollback()
        print("Update Error:", e)
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()
# -----------------------------------------------------------
# ADMIN LOGS ROUTE  
@app.route("/admin/logs", methods=["GET"])
@jwt_required()
def get_admin_logs():
    session = Session()
    try:
        current_user = session.query(User).filter_by(
            username=get_jwt_identity()
        ).first()

        if not current_user or current_user.role != "admin":
            return jsonify({"error": "Admin access required"}), 403

        logs = session.query(PredictionHistory).order_by(
            PredictionHistory.id.desc()
        ).all()

        return jsonify([
            {
                "id": log.id,                  # 🟢 REQUIRED: Fixes "ID missing" error
                "date": log.timestamp,
                "user": log.user.username if log.user else "Unknown",
                "role": log.top_role,          # 🟢 RENAMED: Matches frontend expectations
                "confidence": log.confidence,
                "rating": log.user_rating,
                "feedback": log.user_feedback,
                "flag": log.admin_flag         # 🟢 REQUIRED: Shows "Reviewed" badge
            }
            for log in logs
        ]), 200
    except Exception as e:
        print("Log Error:", e)
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()
# -----------------------------------------------------------
# RUN APP
# -----------------------------------------------------------
# FLAG PREDICTION ROUTE (Required for Admin Panel)
# -----------------------------------------------------------
@app.route("/admin/flag", methods=["POST"])
@jwt_required()
def flag_prediction():
    session = Session()
    try:
        # 1. Verify Admin
        current_user = session.query(User).filter_by(
            username=get_jwt_identity()
        ).first()

        if not current_user or current_user.role != "admin":
            return jsonify({"error": "Admin access required"}), 403

        # 2. Get ID from request
        data = request.get_json()
        log_id = data.get("log_id")

        if not log_id:
            return jsonify({"error": "Log ID required"}), 400

        # 3. Find and Update Log
        log_entry = session.query(PredictionHistory).filter_by(id=log_id).first()
        if not log_entry:
            return jsonify({"error": "Log entry not found"}), 404

        log_entry.admin_flag = "flagged"
        session.commit()

        return jsonify({"message": "Prediction flagged successfully"}), 200

    except Exception as e:
        session.rollback()
        print("Flag Error:", e)
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

# -----------------------------------------------------------
# SUBMIT FEEDBACK ROUTE
# -----------------------------------------------------------
@app.route("/submit-feedback", methods=["POST"])
@jwt_required()
def submit_feedback():
    session = Session()
    try:
        data = request.get_json()
        log_id = data.get("history_id")
        rating = data.get("rating")
        comments = data.get("comments")

        if not log_id or not rating:
            return jsonify({"error": "Missing ID or Rating"}), 400

        # Find the prediction history entry
        log_entry = session.query(PredictionHistory).filter_by(id=log_id).first()
        
        if not log_entry:
            return jsonify({"error": "History record not found"}), 404

        # Update feedback
        log_entry.user_rating = int(rating)
        log_entry.user_feedback = comments
        session.commit()

        return jsonify({"message": "Feedback saved"}), 200

    except Exception as e:
        session.rollback()
        print("Feedback Error:", e)
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


if __name__ == "__main__":
    app.run(debug=True, port=5000)