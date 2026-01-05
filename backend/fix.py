import pandas as pd
import os

# ---------------------------------------------------------
# 1. SETUP
# ---------------------------------------------------------
FILE_PATH = r"D:\infosys\job_role_preditor\dataset\education_career_success.csv"
print(f"📂 Processing: {FILE_PATH}")

if os.path.exists(FILE_PATH):
    df = pd.read_csv(FILE_PATH)
    
    # ---------------------------------------------------------
    # 2. INTELLIGENT FORCE FIX
    # ---------------------------------------------------------
    print("\n🔧 Scanning every single row...")
    
    # Define a function to fix GPA row-by-row
    def normalize_gpa(gpa):
        try:
            val = float(gpa)
            # If it looks like a 4.0 scale score (e.g., 3.8), convert it
            if val <= 4.0:
                return val * 2.5
            # If it's already big (e.g., 8.5), keep it
            return val
        except:
            return 0.0 # Handle bad data
            
    # Apply this logic to the ENTIRE 'University_GPA' column
    # (We assume the new generated data is > 6.0, so this won't hurt it)
    df['University_GPA'] = df['University_GPA'].apply(normalize_gpa)
    
    print("✅ Converted all values ≤ 4.0 to the 10.0 scale.")

    # ---------------------------------------------------------
    # 3. SHUFFLE & SAVE
    # ---------------------------------------------------------
    # Shuffle just to be safe
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    df.to_csv(FILE_PATH, index=False)
    
    print("\n" + "="*50)
    print(f"✅ SUCCESS! File Forced-Fixed: {FILE_PATH}")
    print("="*50)
    print("👉 Go to Admin Panel -> Upload -> Retrain.")
    
else:
    print("❌ Error: File not found.")