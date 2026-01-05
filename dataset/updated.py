import pandas as pd
import numpy as np
import random
import os

# ---------------------------------------------------------
# 1. SETUP PATHS
# ---------------------------------------------------------
# Source File (Where we get the top 400 rows)
OLD_FILE_PATH = r"D:\infosys\job_role_preditor\dataset\education_career_success.csv"

# Target File (Where we save the final shuffled data - AS YOU REQUESTED)
NEW_FILE_PATH = r"D:\infosys\job_role_preditor\dataset\education_career_success_UPDATED.csv"

print(f"📂 Reading from: {OLD_FILE_PATH}")
print(f"💾 Saving to:   {NEW_FILE_PATH}")

# ---------------------------------------------------------
# 2. LOAD & CLEAN OLD DATA
# ---------------------------------------------------------
cols = ['Degree', 'Field_of_Study', 'University_GPA', 'Certifications', 'Internships_Completed', 'Job_Role']
old_rows = []

if os.path.exists(OLD_FILE_PATH):
    try:
        df_old = pd.read_csv(OLD_FILE_PATH)
        
        # Keep top 401 rows (History)
        df_keep = df_old.iloc[:401].copy()
        
        # --- FIX: REMOVE ROWS WITH NO JOB ROLE ---
        df_keep = df_keep.dropna(subset=['Job_Role'])
        df_keep = df_keep[df_keep['Job_Role'].astype(str).str.strip() != ""]
        
        # Fix missing columns
        for c in cols:
            if c not in df_keep.columns:
                df_keep[c] = ""
                
        old_rows = df_keep[cols].values.tolist()
        print(f"✅ Loaded Old Data: Kept {len(old_rows)} valid rows.")
        
    except Exception as e:
        print(f"⚠️ Error reading old file: {e}")
else:
    print("⚠️ Old file not found. Starting fresh.")

# ---------------------------------------------------------
# 3. GENERATE NEW DATA (120 ROWS/COURSE + SMART LOGIC)
# ---------------------------------------------------------
print("🚀 Generating 120 new rows per course...")

curriculum = {
    "CS & IT": {
        "degree_label": "B.Tech",
        "degrees": ["Computer Science Engineering", "Information Technology", "AI & Machine Learning", "AI & Data Science", "Cybersecurity", "Data Science"],
        "roles": ["AI Engineer", "Data Scientist", "Full Stack Developer", "Software Engineer", "Backend Developer", "Frontend Developer", "Cybersecurity Analyst", "System Engineer"]
    },
    "Electronics": {
        "degree_label": "B.Tech",
        "degrees": ["Electronics & Communication Engineering", "Electrical & Electronics Engineering", "Electrical Engineering", "Instrumentation Engineering"],
        "roles": ["VLSI Design Engineer", "Embedded Systems Engineer", "Control Systems Engineer", "Network Engineer", "Maintenance Engineer"]
    },
    "Core Engineering": {
        "degree_label": "B.Tech",
        "degrees": ["Mechanical Engineering", "Civil Engineering", "Chemical Engineering", "Production Engineering", "Metallurgical Engineering", "Mining Engineering"],
        "roles": ["Project Manager", "Structural Engineer", "Process Engineer", "Mechanical Design Engineer", "Site Supervisor"]
    },
    "Specialized Engineering": {
        "degree_label": "B.Tech",
        "degrees": ["Robotics & Automation", "Biotechnology", "Biomedical Engineering", "Aerospace Engineering", "Aeronautical Engineering", "Automobile Engineering", "Mechatronics Engineering", "Marine Engineering", "Petroleum Engineering", "Food Technology", "Textile Engineering", "Environmental Engineering", "Agriculture Engineering"],
        "roles": ["Robotics Engineer", "Biomedical Engineer", "Automotive Design Engineer", "Marine Engineer", "Food Safety Officer"]
    },
    "Management (UG)": {
        "degree_label": "BBA",
        "degrees": ["Finance", "Marketing", "Human Resource Management", "Business Analytics", "International Business", "Logistics & Supply Chain", "Operations Management", "Entrepreneurship", "Digital Marketing"],
        "roles": ["Business Analyst", "Marketing Executive", "HR Generalist", "Operations Coordinator", "Sales Manager"]
    },
    "Service Sector": {
        "degree_label": "BBA",
        "degrees": ["Hospitality Management", "Travel & Tourism", "Retail Management", "Banking & Insurance", "Aviation Management", "Healthcare Management"],
        "roles": ["Hotel Manager", "Retail Store Manager", "Aviation Operations Manager", "Hospital Administrator", "Relationship Manager"]
    },
    "Management (PG)": {
        "degree_label": "MBA",
        "degrees": ["Finance (Advanced)", "Marketing (Advanced)", "Human Resource (Advanced)", "Business Analytics (Advanced)", "International Business (Advanced)", "Operations Management (Advanced)", "IT Management", "Entrepreneurship (Advanced)", "Digital Marketing (Advanced)"],
        "roles": ["Investment Banker", "Product Manager", "HR Director", "Management Consultant", "Business Development Manager"]
    },
    "Specialized Management": {
        "degree_label": "MBA",
        "degrees": ["Logistics & Supply Chain (Advanced)", "Hospitality & Tourism (Advanced)", "Healthcare Management (Advanced)", "Retail Management (Advanced)", "Banking & Financial Services", "Agri-Business Management", "Aviation Management (Advanced)"],
        "roles": ["Supply Chain Manager", "Hospital Administrator", "Portfolio Manager", "Retail Operations Head", "Agri-Business Manager"]
    },
    "Design": {
        "degree_label": "B.Des",
        "degrees": ["Fashion Design", "Interior Design", "Product Design", "Communication Design", "Graphic Design", "UI/UX Design", "Industrial Design", "Animation & Multimedia", "Game Design", "Textile Design", "Jewellery Design"],
        "roles": ["UI/UX Designer", "Product Designer", "Fashion Stylist", "Game Artist", "Interior Architect"]
    },
    "Humanities": {
        "degree_label": "B.A",
        "degrees": ["English", "Psychology", "Sociology", "Economics", "Political Science", "History", "Geography", "Philosophy", "Education", "Hindi", "Tamil", "Sanskrit"],
        "roles": ["Content Writer", "Psychologist", "Policy Analyst", "Teacher", "Social Worker"]
    },
    "Creative Arts": {
        "degree_label": "B.A",
        "degrees": ["Journalism & Mass Communication", "Public Administration", "Fine Arts", "Performing Arts"],
        "roles": ["Journalist", "Public Relations Officer", "Art Director", "Civil Servant", "Media Planner"]
    },
    "Commerce": {
        "degree_label": "B.Com",
        "degrees": ["Accounting & Finance", "Banking & Insurance", "Taxation", "Auditing", "Computer Applications", "Business Analytics", "Economics", "Financial Markets", "International Business", "Corporate Secretaryship"],
        "roles": ["Chartered Accountant", "Financial Auditor", "Tax Consultant", "Investment Analyst", "Bank Officer"]
    },
    "Tech & Science": {
        "degree_label": "B.Sc",
        "degrees": ["Computer Science", "Information Technology", "Data Science", "Artificial Intelligence", "Mathematics", "Physics", "Chemistry", "Electronics", "Statistics", "Forensic Science"],
        "roles": ["Software Developer", "Lab Technician", "Data Analyst", "Research Assistant", "Forensic Expert"]
    },
    "Life Sciences": {
        "degree_label": "B.Sc",
        "degrees": ["Biotechnology", "Microbiology", "Agriculture", "Environmental Science", "Psychology", "Nutrition & Dietetics", "Fashion Design", "Nursing"],
        "roles": ["Clinical Research Associate", "Microbiologist", "Dietician", "Agricultural Officer", "Registered Nurse"]
    },
    "Masters Engineering": {
        "degree_label": "M.Tech",
        "degrees": ["Computer Science Engineering (Masters)", "Information Technology (Masters)", "Data Science (Masters)", "Artificial Intelligence (Masters)", "Machine Learning", "Cybersecurity (Masters)", "VLSI", "Embedded Systems", "Power Systems", "Thermal Engineering", "Structural Engineering", "Robotics", "Biotechnology (Masters)", "Environmental Engineering (Masters)", "Mechanical Design", "Manufacturing Engineering", "Transportation Engineering"],
        "roles": ["R&D Engineer", "Senior Data Scientist", "VLSI Architect", "Structural Consultant", "Robotics System Architect"]
    },
    "Masters Science": {
        "degree_label": "M.Sc",
        "degrees": ["Computer Science (M.Sc)", "Information Technology (M.Sc)", "Mathematics (M.Sc)", "Physics (M.Sc)", "Chemistry (M.Sc)", "Electronics (M.Sc)", "Data Science (M.Sc)", "Artificial Intelligence (M.Sc)", "Statistics (M.Sc)", "Biotechnology (M.Sc)", "Microbiology (M.Sc)", "Agriculture (M.Sc)", "Environmental Science (M.Sc)", "Psychology (M.Sc)", "Food Science & Nutrition", "Forensic Science (M.Sc)"],
        "roles": ["Senior Researcher", "Data Engineer", "Clinical Psychologist", "Food Scientist", "Statistician"]
    }
}

new_data = []

for category, info in curriculum.items():
    degree_lbl = info['degree_label']
    roles = info['roles']
    
    for course in info['degrees']:
        for _ in range(150): # 120 rows per course
            gpa = round(random.uniform(6.0, 9.9), 2)
            certs = random.choice(["None", "Python", "Java", "AWS", "CPA", "React", "Scrum Master", "Six Sigma", "AutoCAD"])
            internship = random.randint(0, 3)
            
            # Smart Assignment (Higher GPA = Top Role)
            if gpa >= 9.0: role = roles[0]
            elif gpa >= 8.0: role = roles[1] if len(roles) > 1 else roles[0]
            elif gpa >= 7.0: role = roles[2] if len(roles) > 2 else roles[-1]
            else: role = roles[-1]
            
            new_data.append([degree_lbl, course, gpa, certs, internship, role])

# ---------------------------------------------------------
# 4. MERGE, SHUFFLE & SAVE
# ---------------------------------------------------------
all_rows = old_rows + new_data
df_final = pd.DataFrame(all_rows, columns=cols)

# --- CRITICAL FIX: SHUFFLE EVERYTHING ---
df_final = df_final.sample(frac=1, random_state=42).reset_index(drop=True)

# Save to the UPDATED path
os.makedirs(os.path.dirname(NEW_FILE_PATH), exist_ok=True)
df_final.to_csv(NEW_FILE_PATH, index=False)

print("\n" + "="*50)
print(f"✅ SUCCESS! File Created: {NEW_FILE_PATH}")
print(f"📊 Total Rows: {len(df_final)}")
print("="*50)
print("👉 VERIFICATION (First 5 Rows should be mixed):")
print(df_final[['Degree', 'Field_of_Study']].head(5))
print("\n👉 NOW: Go to Admin Panel -> Upload 'education_career_success_UPDATED.csv' -> Retrain.")