import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from dotenv import load_dotenv

load_dotenv()

# for now its the local db, database url will be different when deployed
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://incident:changeme@localhost:5432/incidents"
)

# defines db type (postgres), and setup instructions thru its url
engine = create_engine(DATABASE_URL)

# defining SessionLocal to be how we create new database session
# db = SessionLocal()
# we can do queries, adding, commiting with this:
# user = db.query(User).first
# db.add(new_user)
# db.commit()
#
# no autoflush means we have to explicitly "save" changes
SessionLocal = sessionmaker(bind=engine, autoflush=False)

# base class for all database tables
class Base(DeclarativeBase):
    pass

# basically creates a session, lets a function use db, then closes the session after that function is done
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()