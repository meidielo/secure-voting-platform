import os
import sys
from pathlib import Path
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

# Add parent directory to Python path to import app modules
parent_dir = str(Path(__file__).parent.parent.absolute())
sys.path.append(parent_dir)

from app import create_app, db
from app.models import ElectoralRoll
from app.security.encryption import ChaChaEncryptionService

def decrypt_with_fernet(key, data):
    """Decrypt data using Fernet."""
    if data is None:
        return None

    try:
        # Handle URL-safe base64 encoding differences
        if isinstance(data, str):
            # Add padding if needed
            padding_needed = len(data) % 4
            if padding_needed:
                data += '=' * (4 - padding_needed)
            data = data.encode()
        
        # Ensure key is in correct Fernet format
        if isinstance(key, str):
            # Add padding if needed for key
            padding_needed = len(key) % 4
            if padding_needed:
                key += '=' * (4 - padding_needed)
            key = key.encode()
        
        f = Fernet(key)
        decrypted = f.decrypt(data)
        return decrypted.decode()
    except Exception as e:
        print(f"Error decrypting with Fernet: {e}")
        return None

def encrypt_with_chacha(key_b64, data):
    """Encrypt data using the app's ChaCha service to ensure identical format."""
    if data is None:
        return None

    try:
        # Initialize (or re-initialize) service with provided key to ensure consistency
        if key_b64:
            # normalize padding for base64 input
            if isinstance(key_b64, str):
                pad = len(key_b64) % 4
                if pad:
                    key_b64 += '=' * (4 - pad)
            ChaChaEncryptionService.initialize(key_b64)

        service = ChaChaEncryptionService.get_instance()
        # The service handles str conversion and returns standard Base64 with proper padding
        return service.encrypt(data)
    except Exception as e:
        print(f"Error encrypting with ChaCha service: {e}")
        return None

def migrate_encryption():
    """Migrate from Fernet to ChaCha20-Poly1305 encryption."""
    # Get both the old Fernet key and new ChaCha20-Poly1305 key
    old_key = os.environ.get('OLD_FERNET_KEY')
    new_key = os.environ.get('VOTER_PII_KEY_BASE64')
    
    if not old_key:
        print("Error: OLD_FERNET_KEY environment variable not set")
        return
    if not new_key:
        print("Error: VOTER_PII_KEY_BASE64 environment variable not set")
        return

    app = create_app()
    with app.app_context():
        print("Starting encryption migration...")
        
        # Get all electoral roll entries
        entries = ElectoralRoll.query.all()
        total = len(entries)
        print(f"Found {total} electoral roll entries to migrate")

        success_count = 0
        error_count = 0

        for i, entry in enumerate(entries, 1):
            print(f"\rProcessing entry {i}/{total}...", end="", flush=True)
            
            # Get the raw encrypted values from the database
            raw_values = {
                'driver_license_number': entry.driver_license_number,
                'full_name': entry.full_name,
                'address_line1': entry.address_line1,
                'address_line2': entry.address_line2,
                'suburb': entry.suburb,
                'state': entry.state,
                'postcode': entry.postcode
            }

            try:
                # Decrypt all values using Fernet
                decrypted_values = {}
                for field, value in raw_values.items():
                    if value is not None:
                        decrypted = decrypt_with_fernet(old_key, value)
                        if decrypted is None:
                            raise ValueError(f"Could not decrypt {field}")
                        decrypted_values[field] = decrypted

                # Re-encrypt all values using ChaCha20-Poly1305
                for field, value in decrypted_values.items():
                    encrypted = encrypt_with_chacha(new_key, value)
                    if encrypted is None:
                        raise ValueError(f"Could not encrypt {field}")
                    setattr(entry, field, encrypted)

                # Save changes to the database
                db.session.commit()
                success_count += 1
                
            except Exception as e:
                error_count += 1
                print(f"\nError processing entry {entry.id}: {str(e)}")
                db.session.rollback()
                continue

        print("\n\nMigration completed!")
        print(f"Successfully migrated: {success_count}/{total} entries")
        if error_count > 0:
            print(f"Errors encountered: {error_count} entries")
            print("Please check the logs above for details.")

if __name__ == '__main__':
    migrate_encryption()