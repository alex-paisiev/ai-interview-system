import datetime

from sqlalchemy import JSON, Column, DateTime, String
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(String, primary_key=True, index=True)
    candidate_id = Column(String, index=True)
    job_title = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    session_data = Column(MutableDict.as_mutable(JSON))
