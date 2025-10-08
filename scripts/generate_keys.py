from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization

# 1. Generate a new private key
# Use a key size of 4096 bits for strong security.
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=4096,
)

# 2. Derive the public key from the private key
public_key = private_key.public_key()

# 3. Save the private key to a file in PEM format
# This file is highly sensitive and must be kept secret.
with open("private_key.pem", "wb") as f:
    f.write(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption() # Or use a password
    ))
print("✅ Private key saved to private_key.pem")

# 4. Save the public key to a file in PEM format
# This file can be shared publicly.
with open("public_key.pem", "wb") as f:
    f.write(public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ))
print("✅ Public key saved to public_key.pem")
print("✅ Key pair generation complete.")