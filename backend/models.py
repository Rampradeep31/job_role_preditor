from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from datetime import datetime 

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String)
    
    # ✅ ROLE COLUMN (Required for Admin Panel)
    role = Column(String, default="student") 

    # Personal Info
    phone = Column(String)
    skills = Column(String)
    internship = Column(String)
    duration = Column(String)
    preferred_role = Column(String) 

    # Relationships
    education_records = relationship("Education", back_populates="user", cascade="all, delete-orphan")


class Education(Base):
    __tablename__ = "education"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    degree = Column(String)
    specialization = Column(String)
    cgpa = Column(Float)
    year_of_graduation = Column(Integer)
    university = Column(String)
    certifications = Column(String)

    user = relationship("User", back_populates="education_records")

class PredictionHistory(Base):
    __tablename__ = "prediction_history"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Prediction Data
    top_role = Column(String)
    confidence = Column(String)
    all_recommendations = Column(String)
    
    timestamp = Column(String, default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # ✅ NEW FIELDS FOR DAY 5 (Feedback & Admin Logs)
    user_rating = Column(Integer, default=0)       # 1-5 Stars
    user_feedback = Column(String, default="")     # User Comments
    admin_flag = Column(String, default="normal")  # 'normal', 'flagged'

    # Relationship
    user = relationship("User")