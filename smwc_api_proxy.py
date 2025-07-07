import requests
import time
import datetime

def smwc_api_get(url, params=None, log=None, max_retries=3):
    for attempt in range(max_retries):
        response = requests.get(url, params=params)
        reset_ts = response.headers.get('X-RateLimit-Reset')
        reset_str = ""
        if reset_ts:
            try:
                seconds_until_reset = max(int(reset_ts) - int(time.time()), 0)
                reset_str = f"{seconds_until_reset}s"
            except Exception:
                reset_str = reset_ts
        if log:
            log(
                f"[DEBUG] Response headers: "
                f"X-RateLimit-Limit={response.headers.get('X-RateLimit-Limit')}, "
                f"X-RateLimit-Remaining={response.headers.get('X-RateLimit-Remaining')}, "
                f"X-RateLimit-Reset={reset_str}, "
                f"Status={response.status_code}",
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
                    f"X-RateLimit-Reset={reset_str}, "
                    f"X-RateLimit-Limit={response.headers.get('X-RateLimit-Limit')}, "
                    f"X-RateLimit-Remaining={response.headers.get('X-RateLimit-Remaining')}, "
                    f"Status={response.status_code}. "
                    f"Retrying in {wait_time}s...",
                    level="Error"
                )
            time.sleep(wait_time)
            continue
        response.raise_for_status()
        # ADD THIS DELAY TO AVOID HITTING THE LIMIT
        time.sleep(1.1)  # Sleep a bit more than 1 second to be safe
        return response
    raise Exception("Failed to fetch data from SMWC API after retries.")