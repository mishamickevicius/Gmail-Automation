from pydantic import BaseModel

from fastapi import FastAPI

app = FastAPI()

@app.get('/')
async def root():
    return {"message": "Hello World!"}

@app.get('/scan')
async def scan()