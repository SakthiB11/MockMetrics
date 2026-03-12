from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class Test(Base):
    __tablename__ = "tests"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    date = Column(Date)
    score = Column(Float)
    total_marks = Column(Integer)
    accuracy = Column(Float)
    rank = Column(Integer)
    total_participants = Column(Integer)
    percentile = Column(Float)

    subjects = relationship(
        "Subject",
        back_populates="test",
        cascade="all, delete-orphan",
        lazy="joined"
    )
    questions = relationship(
    "Question",
    back_populates="test",
    cascade="all, delete-orphan",
    lazy="joined"
    )
    


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    score = Column(Float)
    total_marks = Column(Integer)
    accuracy = Column(Float)
    percentage = Column(Float)

    test_id = Column(Integer, ForeignKey("tests.id"))

    test = relationship(
        "Test",
        back_populates="subjects"
    )

 

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer,primary_key = True)
    question_number = Column(Integer)
    subject = Column(String(50))
    topic = Column(String(100))
    difficulty = Column(String(10))   
    status = Column(String(10))       
    time_taken_sec = Column(Integer)
    marks_awarded = Column(Float)

    test_id = Column(Integer, ForeignKey("tests.id"))
    test = relationship("Test", back_populates="questions")
