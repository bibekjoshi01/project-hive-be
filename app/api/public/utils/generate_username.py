import random
import string

def generate_username(base_email: str) -> str:
    prefix = base_email.split("@")[0]
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
    return f"{prefix}_{suffix}"
