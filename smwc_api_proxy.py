import requests
import time
from config_manager import ConfigManager

def get_api_delay():
    """Get current API delay setting from config"""
    config = ConfigManager()
    return config.get("api_delay", 0.8)

def smwc_api_get(url, params=None, log=None):
    delay = get_api_delay()
    
    # DEBUG: Always print API URL to console
    if params:
        import urllib.parse
        full_url = url + "?" + urllib.parse.urlencode(params, doseq=True)
        print(f"\n=== API REQUEST URL ===\n{full_url}\n======================\n")
    
    # Log the full API request URL for debugging
    if log and params:
        import urllib.parse
        full_url = url + "?" + urllib.parse.urlencode(params, doseq=True)
        log(f"[DEBUG] API Request: {full_url}", level="debug")
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()  # Raise exception for bad status codes
        
        # Check if response is valid JSON
        try:
            response.json()  # Test if JSON is valid
        except ValueError as e:
            if log:
                log(f"[ERROR] Invalid JSON response: {e}", level="error")
                log(f"[ERROR] Response text: {response.text[:500]}...", level="error")
            raise Exception(f"Invalid JSON response from API: {e}")
        
    except requests.exceptions.RequestException as e:
        if log:
            log(f"[ERROR] Network error: {e}", level="error")
        raise Exception(f"Network error: {e}")

    # Simplified logging - only show rate limit info when needed
    if log and response.headers.get('X-RateLimit-Remaining'):
        remaining = response.headers.get('X-RateLimit-Remaining', 'Unknown')
        if int(remaining) < 10:  # Only warn when getting low
            log(f"[WRN] Rate limit low: {remaining} requests remaining", level="warning")

    if log:
        log(f"[DEBUG] Waiting {delay:.1f} seconds...", level="debug")

    time.sleep(delay)
    return response
