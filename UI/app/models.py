from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="user")
    created_at = Column(DateTime, default=datetime.utcnow)
    analyses = relationship("Analysis", back_populates="user")

class Analysis(Base):
    __tablename__ = "analyses"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String(255), nullable=False)
    contract_type = Column(String(255), default="-")
    risk_level = Column(String(50), default="-")
    status = Column(String(50), default="Analyzing")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    features = Column(String(255), default="")
    summary = Column(Text, default="")
    classification = Column(Text, default="")
    risk_assessment = Column(Text, default="")
    missing_clauses = Column(Text, default="")
    experts_review = Column(Text, default="")
    suggestions = Column(Text, default="")
    json_result = Column(Text, default="")
    user = relationship("User", back_populates="analyses")
