from fastapi import FastAPI
from database import supabase
app = FastAPI()

@app.get("/")
def root():
    return {"message": "hello"}

@app.get("/incidents")
def get_incidents():
    response = supabase.table("Incidents").select("*").execute()
    return response.data
