import random
from src.config import config

DEFAULT_LAUNCH_OPTIONS = {
    "headless": False
}


DEFAULT_ADDITIONAL_ARGS = [
    "--disable-gpu",
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--disable-blink-features=AutomationControlled"
]


_DEFAULT_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Edge/120.0.0.0"
]

DEFAULT_CONTEXT_SETTINGS = {
    "viewport": {"width": 1920, "height": 1080},
    "user_agent": random.choice(_DEFAULT_USER_AGENTS),
    "proxy": None,
    "ignore_https_errors": True,
    "permissions": ["geolocation", "notifications"],
    "geolocation": {"latitude": 51.5074, "longitude": -0.1278},
    "locale": "en-US",
    "timezone_id": "Europe/London",
    "extra_http_headers": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1"
    }
}
