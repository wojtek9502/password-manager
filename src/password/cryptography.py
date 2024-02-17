import os
import secrets
from base64 import urlsafe_b64encode as b64e, urlsafe_b64decode as b64d

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


# Source https://stackoverflow.com/a/55147077
class CryptographyFernet:
    @staticmethod
    def _derive_key(password: bytes, salt: bytes, iterations: int = 600_000) -> bytes:
        """Derive a secret key from a given password and salt"""
        backend = default_backend()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(), length=32, salt=salt,
            iterations=iterations, backend=backend)
        return b64e(kdf.derive(password))

    def password_encrypt(self, message: bytes, additional_pepper: str, iterations: int = 600_000) -> bytes:
        pepper = os.environ['PASSWORD_ENCRYPT_PEPPER']
        salt = secrets.token_bytes(32)
        additional_pepper = additional_pepper + pepper

        key = self._derive_key(additional_pepper.encode(), salt, iterations)
        fernet_encrypted = Fernet(key).encrypt(message)
        return b64e(
            b'%b%b%b' % (
                salt,
                iterations.to_bytes(4, 'big'),
                b64d(fernet_encrypted),
            )
        )

    def password_decrypt(self, token: bytes, password_to_decrypt: str) -> bytes:
        pepper = os.environ['PASSWORD_ENCRYPT_PEPPER']
        password_to_decrypt = password_to_decrypt + pepper

        decoded = b64d(token)
        salt, iterations, token = decoded[:32], decoded[32:36], b64e(decoded[36:])
        iterations = int.from_bytes(iterations, 'big')
        key = self._derive_key(password_to_decrypt.encode(), salt, iterations)
        return Fernet(key).decrypt(token)
