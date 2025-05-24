import re

def is_valid_phone(phone: str) -> bool:
    return bool(re.fullmatch(r"\+?\d{10,15}", phone))
