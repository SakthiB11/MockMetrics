from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from contextlib import contextmanager

# setting up DB Hardcording username,pwd gotta change it later

engine = create_engine("sqlite:///exam_tracker.db")

Base = declarative_base()

SessionLocal = sessionmaker(bind = engine)

class ManagedSession:
    def __init__(self):
        self.session = SessionLocal()

    def __getattr__(self,name):
        return getattr(self.session, name)

    def __del__(self):
        try:
            self.session.commit()
        except Exception:
            self.session.rollback()
        finally:
            self.session.close()

def get_session():
    return ManagedSession()
  


