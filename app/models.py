from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    gmail_credentials = Column(Text, nullable=True)  # Store credentials as encrypted JSON string

class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    subject = Column(String)
    sender = Column(String)
    received_at = Column(DateTime)
    content = Column(Text)
    ai_analysis = Column(Text)
    recommendation = Column(String)
    user_action = Column(String, nullable=True)
    processed_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="emails")

User.emails = relationship("Email", back_populates="user")
