from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import json

app = FastAPI()

try:
    with open("searches.json", "r") as f:
        searches = json.load(f)
except FileNotFoundError:
    searches = []

class SearchItem(BaseModel):
    location: str
    checkin: str
    checkout: str
    guests: int
    max_price: int
    distance: int

@app.get("/searches")
def get_searches():
    return searches

@app.post("/searches")
def add_search(item: SearchItem):
    searches.append(item.dict())
    with open("searches.json", "w") as f:
        json.dump(searches, f)
    return {"message": "Search added"}

@app.delete("/searches/{index}")
def delete_search(index: int):
    if 0 <= index < len(searches):
        deleted = searches.pop(index)
        with open("searches.json", "w") as f:
            json.dump(searches, f)
        return {"deleted": deleted}
    raise HTTPException(status_code=404, detail="Search not found")
