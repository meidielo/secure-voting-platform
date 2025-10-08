import os
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature

# --- KEY LOADING ---
# In a real app, load these from a secure location (e.g., environment variables or a secrets manager)
# For this project, we'll assume they are in the 'instance' folder.
INSTANCE_FOLDER = os.path.join(os.path.dirname(__file__), '..', '..', 'instance')

try:
    with open(os.path.join(INSTANCE_FOLDER, "private_key.pem"), "rb") as key_file:
        PRIVATE_KEY = serialization.load_pem_private_key(key_file.read(), password=None)

    with open(os.path.join(INSTANCE_FOLDER, "public_key.pem"), "rb") as key_file:
        PUBLIC_KEY = serialization.load_pem_public_key(key_file.read())
except FileNotFoundError:
    PRIVATE_KEY = None
    PUBLIC_KEY = None
    print("WARNING: Key files not found. Signing and verification will fail.")


def sign_data(data: bytes) -> bytes:
    """Signs the given data using the AEC's private key."""
    if not PRIVATE_KEY:
        raise RuntimeError("Private key is not loaded.")
        
    signature = PRIVATE_KEY.sign(
        data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature

def verify_signature(data: bytes, signature: bytes) -> bool:
    """Verifies a signature against the data using the AEC's public key."""
    if not PUBLIC_KEY:
        raise RuntimeError("Public key is not loaded.")

    try:
        PUBLIC_KEY.verify(
            signature,
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except InvalidSignature:
        return False
