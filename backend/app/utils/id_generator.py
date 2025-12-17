import random
import string
import time


def generate_cuid() -> str:
    """
    Generate a CUID-like identifier.
    Format: c + timestamp_base36 + random_chars
    """
    timestamp = int(time.time() * 1000)
    
    # Convert timestamp to base36
    chars = string.digits + string.ascii_lowercase
    timestamp_str = ""
    while timestamp > 0:
        timestamp_str = chars[timestamp % 36] + timestamp_str
        timestamp //= 36
    
    # Generate random characters
    random_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
    
    return f"c{timestamp_str}{random_part}"

