from fastapi import FastAPI, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import engine, Base, get_db
from backend import models

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