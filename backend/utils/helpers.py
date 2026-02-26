import re
from datetime import datetime

def mask_amount(value, bucket=100):
    if value is None:
        return None
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None
    return float(round(value / bucket) * bucket)

def mask_text(text):
    if not text:
        return ""
    text = re.sub(r"\d", "X", text)
    return text[:2000]

def clean_text(text):
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()

def credit_score_from_prob(prob):
    prob = max(0.0, min(1.0, float(prob)))
    return int(300 + prob * 600)

def risk_band_from_score(score):
    if score >= 750:
        return "Low"
    if score >= 650:
        return "Medium"
    return "High"

def confidence_from_prob(prob):
    prob = max(0.0, min(1.0, float(prob)))
    return round(abs(prob - 0.5) * 2, 4)

def parse_date(text):
    if not text:
        return None
    patterns = [
        r"(\d{4})-(\d{2})-(\d{2})",
        r"(\d{2})/(\d{2})/(\d{4})",
        r"(\d{2})-(\d{2})-(\d{4})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            parts = match.groups()
            if len(parts[0]) == 4:
                year, month, day = parts
            else:
                month, day, year = parts
            try:
                return datetime(int(year), int(month), int(day))
            except ValueError:
                continue
    return None
