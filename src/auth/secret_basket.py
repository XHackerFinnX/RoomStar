import hashlib
import secrets

def generate_secret_id(basket_id: int) -> str:
    salt = secrets.token_hex(8)
    base_string = f"{basket_id}-{salt}"
    hash_obj = hashlib.sha256(base_string.encode())
    return hash_obj.hexdigest()[:30]
