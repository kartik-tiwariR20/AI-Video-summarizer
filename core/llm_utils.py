import time
import random
from functools import wraps


def with_retry(max_retries: int = 5, base_delay: float = 3.0):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    is_rate_limit = "429" in str(e) or "rate_limited" in str(e).lower()
                    if is_rate_limit and attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                        print(f"⏳ Rate limited. Retrying in {delay:.1f}s (attempt {attempt+1}/{max_retries})...")
                        time.sleep(delay)
                    else:
                        raise
        return wrapper
    return decorator
