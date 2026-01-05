import pandas as pd
import numpy as np
import random
import os

# ---------------------------------------------------------
# 1. CONFIGURATION (Your Specific Path)
# ---------------------------------------------------------
# Using raw string (r"...") to handle Windows backslashes correctly
DATASET_PATH = r"D:\infosys\job_role_preditor\dataset\education_career_success.csv"

# ---------------------------------------------------------
# 2. DEFINE THE CURRICULUM
# ---------------------------------------------------------
curriculum = {
    "CS & IT": {
        "degree_label": "B.Tech",
        "degrees": [
            "Computer Science Engineering", "Information Technology", 
            "AI & Machine Learning", "AI & Data Science", 
            "Cybersecurity", "Data Science"
        ],
        "roles": ["AI Engineer", "Data Scientist", "Full Stack Developer", "Cybersecurity Analyst", "System Engineer"]
    },
    "Electronics": {
        "degree_label": "B.Tech",
        "degrees": [
            "Electronics & Communication Engineering", "Electrical & Electronics Engineering", 
            "Electrical Engineering", "Instrumentation Engineering"
        ],
        "roles": ["VLSI Design Engineer", "Embedded Systems Engineer", "Control Systems Engineer", "Network Engineer", "Maintenance Engineer"]
    },
    "Core Engineering": {
        "degree_label": "B.Tech",
        "degrees": [
            "Mechanical Engineering", "Civil Engineering", 
            "Chemical Engineering", "Production Engineering",
            "Metallurgical Engineering", "Mining Engineering"
        ],
        "roles": ["Project Manager", "Structural Engineer", "Process Engineer", "Mechanical Design Engineer", "Site Supervisor"]
    },
    "Specialized Engineering": {
        "degree_label": "B.Tech",
        "degrees": [
            "Robotics & Automation", "Biotechnology", "Biomedical Engineering",
            "Aerospace Engineering", "Aeronautical Engineering", 
            "Automobile Engineering", "Mechatronics Engineering",
            "Marine Engineering", "Petroleum Engineering",
            "Food Technology", "Textile Engineering",
            "Environmental Engineering", "Agriculture Engineering"
        ],
        "roles": ["Robotics Engineer", "Biomedical Engineer", "Automotive Design Engineer", "Marine Engineer", "Food Safety Officer"]
    },
    "Management (UG)": {
        "degree_label": "BBA",
        "degrees": [
            "Finance", "Marketing", "Human Resource Management",
            "Business Analytics", "International Business",
            "Logistics & Supply Chain", "Operations Management",
            "Entrepreneurship", "Digital Marketing"
        ],
        "roles": ["Business Analyst", "Marketing Executive", "HR Generalist", "Operations Coordinator", "Sales Manager"]
    },
    "Service Sector": {
        "degree_label": "BBA",
        "degrees": [
            "Hospitality Management", "Travel & Tourism", 
            "Retail Management", "Banking & Insurance",
            "Aviation Management", "Healthcare Management"
        ],
        "roles": ["Hotel Manager", "Retail Store Manager", "Aviation Operations Manager", "Hospital Administrator", "Relationship Manager"]
    },
    "Management (PG)": {
        "degree_label": "MBA",
        "degrees": [
            "Finance (Advanced)", "Marketing (Advanced)", "Human Resource (Advanced)",
            "Business Analytics (Advanced)", "International Business (Advanced)",
            "Operations Management (Advanced)", "IT Management",
            "Entrepreneurship (Advanced)", "Digital Marketing (Advanced)"
        ],
        "roles": ["Investment Banker", "Product Manager", "HR Director", "Management Consultant", "Business Development Manager"]
    },
    "Specialized Management": {
        "degree_label": "MBA",
        "degrees": [
            "Logistics & Supply Chain (Advanced)", "Hospitality & Tourism (Advanced)",
            "Healthcare Management (Advanced)", "Retail Management (Advanced)",
            "Banking & Financial Services", "Agri-Business Management",
            "Aviation Management (Advanced)"
        ],
        "roles": ["Supply Chain Manager", "Hospital Administrator", "Portfolio Manager", "Retail Operations Head", "Agri-Business Manager"]
    },
    "Design": {
        "degree_label": "B.Des",
        "degrees": [
            "Fashion Design", "Interior Design", "Product Design",
            "Communication Design", "Graphic Design", "UI/UX Design",
            "Industrial Design", "Animation & Multimedia",
            "Game Design", "Textile Design", "Jewellery Design"
        ],
        "roles": ["UI/UX Designer", "Product Designer", "Fashion Stylist", "Game Artist", "Interior Architect"]
    },
    "Humanities": {
        "degree_label": "B.A",
        "degrees": [
            "English", "Psychology", "Sociology", "Economics",
            "Political Science", "History", "Geography", "Philosophy",
            "Education", "Hindi", "Tamil", "Sanskrit"
        ],
        "roles": ["Content Writer", "Psychologist", "Policy Analyst", "Teacher", "Social Worker"]
    },
    "Creative Arts": {
        "degree_label": "B.A",
        "degrees": [
            "Journalism & Mass Communication", "Public Administration",
            "Fine Arts", "Performing Arts"
        ],
        "roles": ["Journalist", "Public Relations Officer", "Art Director", "Civil Servant", "Media Planner"]
    },
    "Commerce": {
        "degree_label": "B.Com",
        "degrees": [
            "Accounting & Finance", "Banking & Insurance", "Taxation",
            "Auditing", "Computer Applications", "Business Analytics",
            "Economics", "Financial Markets", "International Business",
            "Corporate Secretaryship"
        ],
        "roles": ["Chartered Accountant", "Financial Auditor", "Tax Consultant", "Investment Analyst", "Bank Officer"]
    },
    "Tech & Science": {
        "degree_label": "B.Sc",
        "degrees": [
            "Computer Science", "Information Technology", "Data Science",
            "Artificial Intelligence", "Mathematics", "Physics",
            "Chemistry", "Electronics", "Statistics", "Forensic Science"
        ],
        "roles": ["Software Developer", "Lab Technician", "Data Analyst", "Research Assistant", "Forensic Expert"]
    },
    "Life Sciences": {
        "degree_label": "B.Sc",
        "degrees": [
            "Biotechnology", "Microbiology", "Agriculture",
            "Environmental Science", "Psychology", 
            "Nutrition & Dietetics", "Fashion Design", "Nursing"
        ],
        "roles": ["Clinical Research Associate", "Microbiologist", "Dietician", "Agricultural Officer", "Registered Nurse"]
    },
    "Masters Engineering": {
        "degree_label": "M.Tech",
        "degrees": [
            "Computer Science Engineering (Masters)", "Information Technology (Masters)",
            "Data Science (Masters)", "Artificial Intelligence (Masters)",
            "Machine Learning", "Cybersecurity (Masters)",
            "VLSI", "Embedded Systems", "Power Systems",
            "Thermal Engineering", "Structural Engineering",
            "Robotics", "Biotechnology (Masters)", "Environmental Engineering (Masters)",
            "Mechanical Design", "Manufacturing Engineering",
            "Transportation Engineering"
        ],
        "roles": ["R&D Engineer", "Senior Data Scientist", "VLSI Architect", "Structural Consultant", "Robotics System Architect"]
    },
    "Masters Science": {
        "degree_label": "M.Sc",
        "degrees": [
            "Computer Science (M.Sc)", "Information Technology (M.Sc)", "Mathematics (M.Sc)",
            "Physics (M.Sc)", "Chemistry (M.Sc)", "Electronics (M.Sc)", "Data Science (M.Sc)",
            "Artificial Intelligence (M.Sc)", "Statistics (M.Sc)", "Biotechnology (M.Sc)",
            "Microbiology (M.Sc)", "Agriculture (M.Sc)", "Environmental Science (M.Sc)",
            "Psychology (M.Sc)", "Food Science & Nutrition", "Forensic Science (M.Sc)"
        ],
        "roles": ["Senior Researcher", "Data Engineer", "Clinical Psychologist", "Food Scientist", "Statistician"]
    }
}

# ---------------------------------------------------------
# 3. GENERATE NEW DATA (150 rows per degree)
# ---------------------------------------------------------
new_data = []
print("🚀 Generating new detailed dataset (150 rows per degree)...")

for category, details in curriculum.items():
    degree_lbl = details["degree_label"]
    
    for degree_field in details["degrees"]:
        # 150 students per degree field
        for _ in range(150): 
            # Random Attributes (Realistic 10.0 Scale)
            gpa = round(random.uniform(6.0, 10.0), 2)
            certifications = random.choice([
                "None", "Python", "AWS", "Google Analytics", "AutoCAD", "C++", 
                "Java", "Six Sigma", "React", "Photoshop", "PMP", "CPA", "CFA", "Scrum Master"
            ])
            internship = random.choice([0, 1, 2])
            
            # Logic: Assign Job Role based on GPA
            possible_roles = details["roles"]
            
            if gpa > 8.5:
                job_role = possible_roles[0] 
            elif gpa > 7.5:
                job_role = possible_roles[1] if len(possible_roles) > 1 else possible_roles[0]
            elif gpa > 6.5:
                job_role = possible_roles[2] if len(possible_roles) > 2 else possible_roles[-1]
            else:
                job_role = possible_roles[-1] 
                
            # Add Degree column as the FIRST column
            new_data.append([degree_lbl, degree_field, gpa, certifications, internship, job_role])

columns = ['Degree', 'Field_of_Study', 'University_GPA', 'Certifications', 'Internships_Completed', 'Job_Role']
new_df = pd.DataFrame(new_data, columns=columns)
print(f"   Generated {len(new_df)} new rows of data.")

# ---------------------------------------------------------
# 4. LOAD, PROCESS OLD DATA, AND MERGE
# ---------------------------------------------------------
final_df = new_df

if os.path.exists(DATASET_PATH):
    print(f"📂 Found existing dataset at: {DATASET_PATH}")
    try:
        old_df = pd.read_csv(DATASET_PATH)
        print(f"   - Original Row Count: {len(old_df)}")
        
        # 1. Keep TOP 400 rows exactly as they are (NO changes to values)
        # We ensure we only keep rows that exist (e.g. if file has <400 rows, keep all)
        keep_count = min(len(old_df), 400)
        df_keep = old_df.iloc[:keep_count].copy()
        print(f"   - Keeping top {keep_count} rows (Historical Data).")
        
        # 2. Handle missing columns by making them EMPTY (as requested)
        for col in columns:
            if col not in df_keep.columns:
                print(f"     - Old data missing '{col}'. Setting to empty.")
                df_keep[col] = "" # Empty string as requested
        
        # Select matching columns order
        df_keep = df_keep[columns]

        # 3. Merge: Old Data (Top) + New Data (Bottom)
        final_df = pd.concat([df_keep, new_df], ignore_index=True)
        print(f"   - Merged Row Count: {len(final_df)}")
        
    except Exception as e:
        print(f"⚠️ Error reading old file: {e}")
        print("   Using only new data.")
else:
    print(f"📂 No existing file found at {DATASET_PATH}. Creating new file.")

# ---------------------------------------------------------
# 5. SAVE
# ---------------------------------------------------------
# Ensure directory exists
os.makedirs(os.path.dirname(DATASET_PATH), exist_ok=True)
final_df.to_csv(DATASET_PATH, index=False)

print("\n✅ SUCCESS!")
print(f"💾 File updated: {DATASET_PATH}")
print(f"📊 Final Total Rows: {len(final_df)}")
print("⚡ NOW: Go to Admin Panel -> Upload this file -> Click 'Retrain Model'.")