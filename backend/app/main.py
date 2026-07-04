from fastapi import FastAPI, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db
import app.models as models

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def root():
    return {"message": "hello"}

# incidents api endpoint
# jsut retrieves all Incident objects in db
# SELECT * FROM incidents;
@app.get("/incidents")
def get_incidents(db: Session = Depends(get_db)):
    return db.scalars(select(models.Incident)).all()
@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    return db.scalars(select(models.Post)).all()
@app.get("/tests")
def get_tests(db: Session = Depends(get_db)):
    return db.scalars(select(models.Test)).all() 