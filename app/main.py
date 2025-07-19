from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import json
from apscheduler.schedulers.background import BackgroundScheduler
import requests
from bs4 import BeautifulSoup
from telegram import Bot

app = FastAPI()

# Carica ricerche salvate
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

bot_token = "6149326983:AAGVSMrGK6xOwf1NvNLNEwYue22tq7hoAhg"
chat_id = 817120408  # Sostituisci col tuo

bot = Bot(token=bot_token)

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

def check_prices():
    for item in searches:
        location = item["location"]
        checkin = item["checkin"]
        checkout = item["checkout"]
        guests = item["guests"]
        max_price = item["max_price"]
        distance = item["distance"]

        link = f"https://www.booking.com/searchresults.html?ss={location}&checkin_year_month_monthday={checkin}&checkout_year_month_monthday={checkout}&group_adults={guests}&no_rooms=1&group_children=0"

        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            response = requests.get(link, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")

            prices = soup.select(".fcab3ed991.bd73d13072")  # classe dei prezzi
            if not prices:
                continue
            for price in prices:
                try:
                    price_int = int(price.text.replace("€", "").replace(",", "").strip())
                    if price_int <= max_price:
                        bot.send_message(chat_id=chat_id, text=f"Trovato alloggio a {location} per {price_int}€!\n{link}")
                        break
                except:
                    continue
        except:
            continue

# Avvio del job ogni 60 minuti
scheduler = BackgroundScheduler()
scheduler.add_job(check_prices, "interval", minutes=2)
scheduler.start()
