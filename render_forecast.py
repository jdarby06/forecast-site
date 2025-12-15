import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime

URL = "https://forecast.weather.gov/MapClick.php?CityName=Rochester&state=NY&site=BUF&lat=43.1687&lon=-77.6158"

def get_forecasts():
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, "html.parser")
    forecast_items = soup.select("#seven-day-forecast .tombstone-container")

    periods, descriptions = [], []
    for item in forecast_items:
        period = item.find(class_="period-name").get_text()
        img = item.find("img")
        full_desc = img["title"] if img else None
        periods.append(period)
        descriptions.append(full_desc)

    forecasts = {}
    i = 0
    while i < len(periods):
        day_name = periods[i].replace(" Night", "")
        if i == 0 and (day_name == "Tonight" or day_name == "Today"):
            day_name = datetime.now().strftime("%A")

        if i == 0 and periods[i] == "Tonight":
            day_desc = "During the day: Daytime forecast has already passed"
            night_desc = descriptions[i].replace(periods[i] + ":", "At night:") if descriptions[i] else ""
            forecasts[day_name] = f"{day_desc}\n\n{night_desc}".strip()
            i += 1
            continue

        day_desc = descriptions[i].replace(periods[i] + ":", "During the day:") if descriptions[i] else ""
        night_desc = ""
        if i+1 < len(periods) and "Night" in periods[i+1]:
            night_desc = descriptions[i+1].replace(periods[i+1] + ":", "At night:")
            i += 2
        else:
            i += 1

        forecasts[day_name] = f"{day_desc}\n\n{night_desc}".strip()

    return forecasts

# --- Streamlit UI ---
st.title("🌤 Rochester Weather Forecast")
st.write("This app scrapes the National Weather Service for Rochester forecasts.")

forecasts = get_forecasts()
days = list(forecasts.keys())

choice = st.selectbox("Choose a day:", days)
st.subheader(choice)
st.write(forecasts[choice])
