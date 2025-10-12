import os
from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, create_engine
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import enum

# Database Configuration
DATABASE_URL = "postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}".format(
    user=os.getenv("POSTGRES_USER", "postgres"),
    password=os.getenv("POSTGRES_PASSWORD", "postmaster2025"),
    host=os.getenv("POSTGRES_HOST", "127.0.0.1"),
    port=os.getenv("POSTGRES_PORT", "5432"),
    db=os.getenv("POSTGRES_DB", "postmaster_db")
)

# Create engine and session
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

# Base class for models
Base = declarative_base()


# Enum for lead_result
class LeadResultEnum(enum.Enum):
    generate_lead = "generate_lead"
    no_lead = "no_lead"


# User table
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(100), nullable=False)
    token_json = Column(JSONB, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


# Email table
class Email(Base):
    __tablename__ = "emails"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    gmail_message_id = Column(String(100), unique=True, nullable=False)
    subject = Column(Text)
    sender_email = Column(String(255), nullable=False)
    sender_name = Column(String(255))
    body_text = Column(Text)
    email_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.now)


# Gmail Agent Dataset table
class GmailAgentDataset(Base):
    __tablename__ = "gmail_agent_dataset"
    
    id = Column(Integer, primary_key=True)
    email_id = Column(Integer, ForeignKey("emails.id", ondelete="CASCADE"), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    model_result = Column(Enum(LeadResultEnum, name="lead_result"), nullable=False)
    user_feedback = Column(Enum(LeadResultEnum, name="lead_result"))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
