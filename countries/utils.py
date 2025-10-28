import io
import random
import requests
from datetime import datetime, timezone
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

COUNTRIES_API = "https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies"
EXCHANGE_API = "https://open.er-api.com/v6/latest/USD"

def fetch_countries_data(timeout=15):
    resp = requests.get(COUNTRIES_API, timeout=timeout)
    resp.raise_for_status()
    return resp.json()

def fetch_exchange_rates(timeout=15):
    resp = requests.get(EXCHANGE_API, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()
    # Expect structure: { "result":"success", "rates": { "USD":1, "NGN":... } }
    rates = data.get("rates")
    if rates is None:
        raise ValueError("Missing rates in exchange API response")
    return rates

def generate_summary_image(total_count, top_countries, last_refreshed_at, path="cache/summary.png"):
    # top_countries: list of dicts with name and estimated_gdp
    # Create simple image
    width, height = 1000, 600
    image = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    # choose a default font; Pillow may not have fancy fonts in environment
    try:
        font_title = ImageFont.truetype("DejaVuSans-Bold.ttf", size=28)
        font_text = ImageFont.truetype("DejaVuSans.ttf", size=18)
    except Exception:
        font_title = ImageFont.load_default()
        font_text = ImageFont.load_default()

    margin = 40
    y = margin
    draw.text((margin, y), f"Countries Summary", font=font_title, fill=(0,0,0))
    y += 40
    draw.text((margin, y), f"Total countries: {total_count}", font=font_text)
    y += 30
    draw.text((margin, y), f"Last refresh: {last_refreshed_at.isoformat()}", font=font_text)
    y += 40
    draw.text((margin, y), "Top 5 countries by estimated GDP:", font=font_text)
    y += 30
    for idx, c in enumerate(top_countries[:5], start=1):
        gdp_str = "N/A" if c["estimated_gdp"] is None else f"{c['estimated_gdp']:,}"
        draw.text((margin, y), f"{idx}. {c['name']} — estimated_gdp: {gdp_str}", font=font_text)
        y += 24

    # Ensure directory exists in default storage path
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    buf.seek(0)
    # Save using default storage to project directory
    # Use local FS path relative to project root
    full_path = PathOrStr(path)
    with open(full_path, "wb") as f:
        f.write(buf.read())
    return full_path

def PathOrStr(p):
    # helper to standardize path construction
    import os
    return os.path.join(os.getcwd(), p)
