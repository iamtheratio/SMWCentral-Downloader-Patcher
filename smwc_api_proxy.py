import requests
import time
from config_manager import ConfigManager

def get_api_delay():
    """Get current API delay setting from config"""
    config = ConfigManager()
    return config.get("api_delay", 0.8)

def smwc_api_get(url, params=None, log=None):
    delay = get_api_delay()
    
    # Log the full API request URL for debugging
    if log and params:
        import urllib.parse
        full_url = url + "?" + urllib.parse.urlencode(params, doseq=True)
        log(f"[DEBUG] API Request: {full_url}", level="debug")
    
    response = requests.get(url, params=params)

    # Simplified logging - only show rate limit info when needed
    if log and response.headers.get('X-RateLimit-Remaining'):
        remaining = response.headers.get('X-RateLimit-Remaining', 'Unknown')
        if int(remaining) < 10:  # Only warn when getting low
            log(f"[WRN] Rate limit low: {remaining} requests remaining", level="warning")

    if log:
        log(f"[DEBUG] Waiting {delay:.1f} seconds...", level="debug")

    time.sleep(delay)
    return response