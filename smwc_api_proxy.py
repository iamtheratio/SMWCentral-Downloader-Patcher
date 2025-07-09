import requests
import time
from config_manager import ConfigManager

def get_api_delay():
    """Get current API delay setting from config"""
    config = ConfigManager()
    return config.get("api_delay", 0.8)

def smwc_api_get(url, params=None, log=None, max_retries=3):
    for attempt in range(max_retries):
        response = requests.get(url, params=params)
        reset_ts = response.headers.get('X-RateLimit-Reset')
        remaining = response.headers.get('X-RateLimit-Remaining')
        delay = get_api_delay()  # Use configurable delay instead of hardcoded 0.8

        # Try to use dynamic delay if possible
        try:
            if reset_ts is not None and remaining is not None:
                seconds_until_reset = max(int(reset_ts) - int(time.time()), 1)
                remaining = int(remaining)
                if remaining > 0 and seconds_until_reset > 0:
                    delay = max(seconds_until_reset / remaining, 0.2)
        except Exception as e:
            if log:
                log(f"[WARN] Could not calculate dynamic delay: {e}", level="debug")

        if log:
            log(
                f"[DEBUG] Response headers: "
                f"X-RateLimit-Limit={response.headers.get('X-RateLimit-Limit')}, "
                f"X-RateLimit-Remaining={remaining}, "
                f"X-RateLimit-Reset={reset_ts}, "
                f"Status={response.status_code}, "
                f"Delay={delay:.2f}s",
                level="debug"
            )
        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After", 1)
            try:
                wait_time = max(float(retry_after), 0) + 1
            except Exception:
                wait_time = 1.5
            if log:
                log(
                    f"[WARN] Rate limited. "
                    f"Retry-After={response.headers.get('Retry-After')}, "
                    f"X-RateLimit-Reset={reset_ts}, "
                    f"X-RateLimit-Limit={response.headers.get('X-RateLimit-Limit')}, "
                    f"X-RateLimit-Remaining={remaining}, "
                    f"Status={response.status_code}. "
                    f"Retrying in {wait_time}s...",
                    level="Error"
                )
            time.sleep(wait_time)
            continue
        response.raise_for_status()
        
        # NEW: Log the delay before sleeping
        if log:
            log(f"[DEBUG] Waiting {delay:.1f} seconds before next request.", level="debug")
        
        time.sleep(delay)
        return response
    raise Exception("Failed to fetch data from SMWC API after retries.")