from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import json
import os
import time
import threading
import requests
import httpx
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")

print("🔧 DEBUG - TOKEN:", bot_token)
print("🔧 DEBUG - CHAT_ID:", chat_id)

app = FastAPI()

searches_file = "searches.json"
try:
    with open(searches_file, "r") as f:
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
    with open(searches_file, "w") as f:
        json.dump(searches, f)
    return {"message": "Search added"}

@app.delete("/searches/{index}")
def delete_search(index: int):
    if 0 <= index < len(searches):
        deleted = searches.pop(index)
        with open(searches_file, "w") as f:
            json.dump(searches, f)
        return {"deleted": deleted}
    raise HTTPException(status_code=404, detail="Search not found")

def send_telegram_message(text: str):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        httpx.post(url, data=payload)
    except Exception as e:
        print(f"Errore invio Telegram: {e}")

def check_booking_prices():
    while True:
        print("🔄 Controllo prezzi Booking...")
        for search in searches:
            location = search["location"]
            checkin = search["checkin"]
            checkout = search["checkout"]
            guests = search["guests"]
            max_price = search["max_price"]
            distance = search["distance"]

            url = f"https://www.booking.com/searchresults.it.html?ss={location}&checkin_year_month_monthday={checkin}&checkout_year_month_monthday={checkout}&group_adults={guests}&selected_currency=EUR"

            try:
                response = requests.get(url)
                soup = BeautifulSoup(response.text, "html.parser")
                prices = soup.find_all("span", class_="fcab3ed991")
                numeric_prices = []

                for price_tag in prices:
                    try:
                        price = int(price_tag.get_text().replace("€", "").replace(".", "").strip())
                        numeric_prices.append(price)
                    except:
                        pass

                if numeric_prices:
                    lowest_price = min(numeric_prices)
                    print(f"📍 {location}: prezzo più basso trovato = {lowest_price} €")
                    
                    # 🔧 Invia sempre il messaggio, anche se il prezzo è più alto
                    message = (
                        f"🏠 {location}\n"
                        f"Prezzo trovato: {lowest_price} €\n"
                        f"Periodo: {checkin} ➜ {checkout}\n"
                        f"(Prezzo max impostato: {max_price} €)"
                    )
                    send_telegram_message(message)
            except Exception as e:
                print(f"Errore durante il controllo per {location}: {e}")

        time.sleep(120)  # ⏱️ Aspetta 2 minuti prima del prossimo check

# Avvia il thread dello scraping in background
threading.Thread(target=check_booking_prices, daemon=True).start()
