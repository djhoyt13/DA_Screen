"""Exam invite model for admin tracking (sent → opened → in progress → completed)."""
from datetime import datetime
import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from backend.database import Base


def new_invite_token():
    return uuid.uuid4().hex


class ExamInvite(Base):
    __tablename__ = "exam_invites"

    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String, unique=True, nullable=False, default=new_invite_token, index=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    sent_at = Column(DateTime, default=datetime.now, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    phone_normalized = Column(String, nullable=True, index=True)
    recruiter_email = Column(String, nullable=True)
    assessment = Column(String, nullable=False, default="ds")

    opened_at = Column(DateTime, nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"), nullable=True)

    submission = relationship("Submission", foreign_keys=[submission_id])
