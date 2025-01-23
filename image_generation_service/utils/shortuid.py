import uuid
import hashlib


# Function to generate a short version of a UID
def generate_short_uid(uid: str, length: int = 8) -> str:
    # Create a hash of the prediction ID and return the first 'length' characters
    hash_object = hashlib.md5(uid.encode())
    short_uid = hash_object.hexdigest()[:length]  # Get a short, fixed-length hash
    return short_uid
