from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import json

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import json
import os
import requests
from bs4 import BeautifulSoup
from apscheduler.schedulers.background import BackgroundScheduler

app = FastAPI()

# Caricamento delle ricerche
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

# Funzione per inviare messaggi Telegram
def send_telegram_message(text):
    token = os.getenv("BOT_TOKEN")
    chat_id = os.getenv("CHAT_ID")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, data=payload)

# Funzione per controllare prezzi su Booking
def check_prices():
    print("⏱️ Avvio controllo prezzi...")
    try:
        with open("searches.json", "r") as f:
            searches_data = json.load(f)
    except FileNotFoundError:
        return

    for s in searches_data:
        location = s["location"]
        checkin = s["checkin"]
        checkout = s["checkout"]
        guests = s["guests"]
        max_price = s["max_price"]

        url = (
            f"https://www.booking.com/searchresults.html?"
            f"ss={location}&"
            f"checkin_year_month_monthday={checkin}&"
            f"checkout_year_month_monthday={checkout}&"
            f"group_adults={guests}&"
            f"no_rooms=1"
        )

        headers = {"User-Agent": "Mozilla/5.0"}

        try:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")
            prices = soup.find_all("span", class_="fcab3ed991")

            for p in prices:
                price_text = p.get_text(strip=True).replace("€", "").replace(",", "").replace(".", "")
                if price_text.isdigit():
                    price = int(price_text)
                    if price <= max_price:
                        send_telegram_message(
                            f"🏨 Offerta trovata per {location} a {price} €!\n{url}"
                        )
                        break
        except Exception as e:
            print(f"Errore scraping: {e}")

# Avvio dello scheduler all'avvio dell'app
@app.on_event("startup")
def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_prices, "interval", minutes=60)
    scheduler.start()

        with open("searches.json", "w") as f:
            json.dump(searches, f)
        return {"deleted": deleted}
    raise HTTPException(status_code=404, detail="Search not found")
