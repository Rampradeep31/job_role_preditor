import json
import random
import os

# 1. SETUP
OUTPUT_FILE = "admin_metrics.json"

# 2. DEFINE MOCK DATA SOURCES
degrees = [
    "Computer Science Engineering", "Information Technology", 
    "Mechanical Engineering", "Civil Engineering", 
    "BBA Finance", "BBA Marketing", "MBA", "B.Des"
]

roles_tech = ["Software Developer", "Data Scientist", "AI Engineer", "Cybersecurity Analyst"]
roles_core = ["Mechanical Design Engineer", "Site Supervisor", "Project Engineer"]
roles_biz = ["Business Analyst", "Marketing Manager", "HR Specialist", "Financial Auditor"]
roles_design = ["UI/UX Designer", "Product Designer", "Graphic Designer"]

# 3. GENERATE 100 DUMMY RECORDS
mock_data = []

print("🚀 Generating 100 sample records for Visualization...")

for _ in range(100):
    # Pick a random degree
    deg = random.choice(degrees)
    
    # Assign a logical role based on degree (simulating a smart model)
    if deg in ["Computer Science Engineering", "Information Technology"]:
        role = random.choice(roles_tech)
    elif deg in ["Mechanical Engineering", "Civil Engineering"]:
        role = random.choice(roles_core)
    elif deg in ["BBA Finance", "BBA Marketing", "MBA"]:
        role = random.choice(roles_biz)
    else:
        role = random.choice(roles_design)
        
    # Random metrics
    gpa = round(random.uniform(6.0, 9.8), 2)
    confidence = round(random.uniform(70.0, 99.9), 1)
    
    mock_data.append({
        "degree": deg,
        "predicted_role": role,
        "cgpa": gpa,
        "confidence_score": confidence
    })

# 4. AGGREGATE DATA FOR CHARTS (The "Insights" Part)

# Chart 1: Role Counts
role_counts = {}
for item in mock_data:
    r = item['predicted_role']
    role_counts[r] = role_counts.get(r, 0) + 1

# Chart 2: Degree vs Role Map
degree_map = {}
for item in mock_data:
    d = item['degree']
    r = item['predicted_role']
    if d not in degree_map: degree_map[d] = {}
    degree_map[d][r] = degree_map[d].get(r, 0) + 1

# 5. SAVE TO JSON
final_output = {
    "total_predictions": 100,
    "distribution_chart": role_counts,
    "degree_map_chart": degree_map,
    "raw_data": mock_data
}

with open(OUTPUT_FILE, "w") as f:
    json.dump(final_output, f, indent=4)

print(f"✅ Success! Sample data saved to '{OUTPUT_FILE}'")
print("📊 You can now use this JSON to build charts on Day 2.")