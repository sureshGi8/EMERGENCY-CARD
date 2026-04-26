from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy import create_engine, Column, String, Integer, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import sessionmaker, Session, relationship, declarative_base
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid

# Configuration
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./emergency_card.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    phone = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    profile = relationship("EmergencyProfile", back_populates="user", uselist=False)

class EmergencyProfile(Base):
    __tablename__ = "emergency_profiles"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), unique=True)
    
    # Personal Info
    age = Column(Integer)
    gender = Column(String)
    blood_group = Column(String)
    height = Column(String)
    weight = Column(String)
    address = Column(Text)
    
    # Medical Info
    medical_conditions = Column(Text)
    allergies = Column(Text)
    medications = Column(Text)
    medical_notes = Column(Text)
    
    # Emergency
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="profile")
    contacts = relationship("EmergencyContact", back_populates="profile", cascade="all, delete-orphan")

class EmergencyContact(Base):
    __tablename__ = "emergency_contacts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_id = Column(String, ForeignKey("emergency_profiles.id"))
    
    name = Column(String, nullable=False)
    relation = Column(String)
    phone = Column(String, nullable=False)
    email = Column(String)
    priority = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    profile = relationship("EmergencyProfile", back_populates="contacts")

class AccessLog(Base):
    __tablename__ = "access_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_id = Column(String)
    accessed_by = Column(String)
    access_type = Column(String)
    ip_address = Column(String)
    location = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic Models
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class ProfileCreate(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    height: Optional[str] = None
    weight: Optional[str] = None
    address: Optional[str] = None
    medical_conditions: Optional[str] = None
    allergies: Optional[str] = None
    medications: Optional[str] = None
    medical_notes: Optional[str] = None

class ContactCreate(BaseModel):
    name: str
    relation: str
    phone: str
    email: Optional[str] = None
    priority: Optional[int] = 1

# FastAPI app
app = FastAPI(title="Emergency Card System", version="2.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Utility functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# Routes

@app.get("/")
async def root():
    return {"message": "Emergency Card API is running", "status": "healthy"}

# Authentication
@app.post("/api/auth/register", response_model=Token)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        phone=user_data.phone
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token = create_access_token(data={"sub": new_user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/auth/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# User Profile
@app.get("/api/user/me")
async def get_current_user_info(token: str, db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "phone": user.phone
    }

# Emergency Profile
@app.get("/api/profile")
async def get_profile(token: str, db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    profile = db.query(EmergencyProfile).filter(EmergencyProfile.user_id == user.id).first()
    
    if not profile:
        return {"profile": None}
    
    return {
        "profile": {
            "id": profile.id,
            "age": profile.age,
            "gender": profile.gender,
            "blood_group": profile.blood_group,
            "height": profile.height,
            "weight": profile.weight,
            "address": profile.address,
            "medical_conditions": profile.medical_conditions,
            "allergies": profile.allergies,
            "medications": profile.medications,
            "medical_notes": profile.medical_notes,
            "is_active": profile.is_active,
            "created_at": profile.created_at,
            "updated_at": profile.updated_at
        }
    }

@app.post("/api/profile")
async def create_or_update_profile(
    profile_data: ProfileCreate,
    token: str,
    db: Session = Depends(get_db)
):
    user = get_current_user(token, db)
    profile = db.query(EmergencyProfile).filter(EmergencyProfile.user_id == user.id).first()
    
    if profile:
        for key, value in profile_data.dict(exclude_unset=True).items():
            setattr(profile, key, value)
        profile.updated_at = datetime.utcnow()
    else:
        profile = EmergencyProfile(
            user_id=user.id,
            **profile_data.dict(exclude_unset=True)
        )
        db.add(profile)
    
    db.commit()
    db.refresh(profile)
    
    return {
        "message": "Profile saved successfully",
        "profile_id": profile.id
    }

# Emergency Contacts
@app.get("/api/contacts")
async def get_contacts(token: str, db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    profile = db.query(EmergencyProfile).filter(EmergencyProfile.user_id == user.id).first()
    
    if not profile:
        return {"contacts": []}
    
    contacts = db.query(EmergencyContact).filter(
        EmergencyContact.profile_id == profile.id
    ).order_by(EmergencyContact.priority).all()
    
    return {
        "contacts": [
            {
                "id": c.id,
                "name": c.name,
                "relation": c.relation,
                "phone": c.phone,
                "email": c.email,
                "priority": c.priority
            }
            for c in contacts
        ]
    }

@app.post("/api/contacts")
async def add_contact(
    contact_data: ContactCreate,
    token: str,
    db: Session = Depends(get_db)
):
    user = get_current_user(token, db)
    profile = db.query(EmergencyProfile).filter(EmergencyProfile.user_id == user.id).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Please create your profile first")
    
    new_contact = EmergencyContact(
        profile_id=profile.id,
        **contact_data.dict()
    )
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    
    return {
        "message": "Contact added successfully",
        "contact": {
            "id": new_contact.id,
            "name": new_contact.name,
            "relation": new_contact.relation,
            "phone": new_contact.phone,
            "email": new_contact.email,
            "priority": new_contact.priority
        }
    }

@app.delete("/api/contacts/{contact_id}")
async def delete_contact(
    contact_id: str,
    token: str,
    db: Session = Depends(get_db)
):
    user = get_current_user(token, db)
    profile = db.query(EmergencyProfile).filter(EmergencyProfile.user_id == user.id).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    contact = db.query(EmergencyContact).filter(
        EmergencyContact.id == contact_id,
        EmergencyContact.profile_id == profile.id
    ).first()
    
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    db.delete(contact)
    db.commit()
    
    return {"message": "Contact deleted successfully"}

# Get Card Data as JSON (for frontend display)
@app.get("/api/card/data")
async def get_card_data(token: str, db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    profile = db.query(EmergencyProfile).filter(EmergencyProfile.user_id == user.id).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    contacts = db.query(EmergencyContact).filter(
        EmergencyContact.profile_id == profile.id
    ).order_by(EmergencyContact.priority).all()
    
    primary_contact = None
    if contacts:
        primary_contact = {
            "name": contacts[0].name,
            "phone": contacts[0].phone
        }
    
    # Log access
    access_log = AccessLog(
        profile_id=profile.id,
        accessed_by="Self View",
        access_type="Dashboard Card View",
        ip_address="",
        location=""
    )
    db.add(access_log)
    db.commit()
    
    return {
        "user_name": user.full_name,
        "age": profile.age or "N/A",
        "blood_group": profile.blood_group or "Unknown",
        "primary_contact": primary_contact,
        "profile_id": profile.id
    }

# Type 1 Card - Detailed View (for QR code scanning)
@app.get("/emergency/{profile_id}/type1", response_class=HTMLResponse)
async def view_emergency_card_type1(profile_id: str, db: Session = Depends(get_db)):
    profile = db.query(EmergencyProfile).filter(EmergencyProfile.id == profile_id).first()
    
    if not profile:
        return "<html><body><h2>Card not found</h2></body></html>"
    
    user = db.query(User).filter(User.id == profile.user_id).first()
    contacts = db.query(EmergencyContact).filter(
        EmergencyContact.profile_id == profile.id
    ).order_by(EmergencyContact.priority).all()
    
    # Log access
    access_log = AccessLog(
        profile_id=profile.id,
        accessed_by="QR Scan",
        access_type="Emergency Card Access (Type 1)",
        ip_address="",
        location=""
    )
    db.add(access_log)
    db.commit()
    
    # Gender HTML
    gender_html = ''
    if profile.gender:
        gender_html = f'''<div class="detail-item">
                <span class="detail-label">Gender:</span>
                <span class="detail-value">{profile.gender}</span>
            </div>'''
    
    # Allergies HTML
    allergies_html = ''
    if profile.allergies:
        allergies_html = f'''<div class="section">
            <div class="section-title">Allergies</div>
            <div class="info-text">{profile.allergies}</div>
        </div>'''
    
    # Conditions HTML
    conditions_html = ''
    if profile.medical_conditions:
        conditions_html = f'''<div class="section">
            <div class="section-title">Medical Conditions</div>
            <div class="info-text">{profile.medical_conditions}</div>
        </div>'''
    
    # Medications HTML
    medications_html = ''
    if profile.medications:
        medications_html = f'''<div class="section">
            <div class="section-title">Medications</div>
            <div class="info-text">{profile.medications}</div>
        </div>'''
    
    # Contacts HTML
    contacts_html = ''
    for c in contacts:
        contacts_html += f'''
        <div class="contact-card">
            <div class="contact-name">
                {c.name} <span class="contact-relation">({c.relation})</span>
            </div>
            <div class="action-buttons">
                <a href="tel:{c.phone}" class="btn btn-call">📞 Call {c.phone}</a>
                <a href="sms:{c.phone}?body=Emergency!" class="btn btn-sms">📱 Send SMS</a>
                <a href="https://wa.me/{c.phone.replace('+', '').replace(' ', '')}?text=Emergency!" 
                   class="btn btn-whatsapp">💬 WhatsApp</a>
            </div>
        </div>'''
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Emergency Medical Info - {user.full_name}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f5f5;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 15px;
        }}
        .emergency-card {{
            width: 100%;
            max-width: 380px;
            background: #ffffff;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
        }}
        .card-header {{
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
            padding: 24px 20px;
            text-align: center;
            color: white;
        }}
        .card-header h1 {{
            font-size: 20px;
            font-weight: 800;
            letter-spacing: 1px;
            margin-bottom: 4px;
        }}
        .card-header p {{
            font-size: 12px;
            opacity: 0.95;
            font-weight: 500;
        }}
        .card-body {{ padding: 20px; }}
        .section {{ margin-bottom: 16px; }}
        .section-title {{
            font-size: 14px;
            font-weight: 800;
            color: #000000;
            margin-bottom: 8px;
        }}
        .detail-item {{
            background: #f3f3f3;
            border-radius: 6px;
            padding: 10px 12px;
            margin-bottom: 6px;
            font-size: 13px;
            color: #222;
            display: flex;
            justify-content: space-between;
        }}
        .detail-label {{ font-weight: 600; color: #000; }}
        .detail-value {{ font-weight: 400; color: #333; }}
        .blood-group-wrapper {{
            display: flex;
            justify-content: center;
            margin-top: 8px;
        }}
        .blood-group-badge {{
            background: linear-gradient(135deg, #dc2626, #b91c1c);
            color: white;
            padding: 12px 40px;
            border-radius: 30px;
            font-size: 24px;
            font-weight: 900;
            letter-spacing: 2px;
            box-shadow: 0 4px 12px rgba(220, 38, 38, 0.4);
        }}
        .info-text {{
            background: #fef2f2;
            border-left: 4px solid #dc2626;
            border-radius: 6px;
            padding: 10px 12px;
            font-size: 13px;
            color: #222;
            line-height: 1.5;
        }}
        .emergency-contacts {{
            margin-top: 20px;
            padding-top: 16px;
            border-top: 2px solid #e5e5e5;
        }}
        .contact-card {{
            background: #f0fdf4;
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 12px;
        }}
        .contact-name {{
            font-size: 14px;
            font-weight: 700;
            color: #000;
            margin-bottom: 8px;
        }}
        .contact-relation {{
            font-size: 12px;
            color: #666;
            font-weight: 500;
        }}
        .action-buttons {{
            display: flex;
            flex-direction: column;
            gap: 8px;
            margin-top: 10px;
        }}
        .btn {{
            padding: 12px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 700;
            text-align: center;
            text-decoration: none;
            color: white;
            transition: 0.2s ease;
        }}
        .btn-call {{ background: #16a34a; }}
        .btn-sms {{ background: #f59e0b; }}
        .btn-whatsapp {{ background: #25d366; }}
        .btn:active {{ opacity: 0.8; transform: scale(0.98); }}
        @media (max-width: 400px) {{
            .card-header h1 {{ font-size: 18px; }}
            .blood-group-badge {{ font-size: 20px; padding: 10px 32px; }}
        }}
    </style>
</head>
<body>
<div class="emergency-card">
    <div class="card-header">
        <h1>EMERGENCY MEDICAL INFO</h1>
        <p>For First Responders</p>
    </div>
    <div class="card-body">
        <div class="section">
            <div class="section-title">Personal Details</div>
            <div class="detail-item">
                <span class="detail-label">Name:</span>
                <span class="detail-value">{user.full_name}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Age:</span>
                <span class="detail-value">{profile.age or 'Not specified'}</span>
            </div>
            {gender_html}
        </div>
        <div class="section">
            <div class="section-title">Blood Group</div>
            <div class="blood-group-wrapper">
                <div class="blood-group-badge">{profile.blood_group or 'Unknown'}</div>
            </div>
        </div>
        {allergies_html}
        {conditions_html}
        {medications_html}
        <div class="emergency-contacts">
            <div class="section-title">Emergency Contacts</div>
            {contacts_html}
        </div>
    </div>
</div>
</body>
</html>'''
    
    return html

# Access Logs
@app.get("/api/logs")
async def get_access_logs(token: str, db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    profile = db.query(EmergencyProfile).filter(EmergencyProfile.user_id == user.id).first()
    
    if not profile:
        return {"logs": []}
    
    logs = db.query(AccessLog).filter(
        AccessLog.profile_id == profile.id
    ).order_by(AccessLog.timestamp.desc()).limit(50).all()
    
    return {
        "logs": [
            {
                "id": log.id,
                "accessed_by": log.accessed_by,
                "access_type": log.access_type,
                "timestamp": log.timestamp
            }
            for log in logs
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
