import os

from src.password.cryptography import CryptographyFernet
from tests.api.ApiBaseTests import ApiBaseTest


class CryptographyFernetTest(ApiBaseTest):
    def test_encrypt(self):
        # given
        crypt_fernet = CryptographyFernet()
        iterations = 480_000
        message = 'test'.encode()
        master_password = 'secret_master_password'

        # when
        password_encrypt = crypt_fernet.password_encrypt(message=message, password=master_password, iterations=iterations)

        # then
        assert password_encrypt
        assert type(password_encrypt) == bytes
        assert password_encrypt != message

    def test_encrypt_and_encrypt(self):
        # given
        crypt_fernet = CryptographyFernet()
        iterations = 480_000
        message = 'test'
        master_password = 'secret_master_password'

        # when - encrypt
        password_encrypt = crypt_fernet.password_encrypt(message=message.encode(), password=master_password, iterations=iterations)

        # then
        assert password_encrypt
        assert type(password_encrypt) == bytes
        assert password_encrypt != message

        # when - decrypt
        password_decrypt = crypt_fernet.password_decrypt(token=password_encrypt, password=master_password)
        assert password_decrypt
        assert type(password_decrypt) == bytes
        assert password_decrypt.decode() == message