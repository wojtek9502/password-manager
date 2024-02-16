import os

from src.password.cryptography import CryptographyFernet
from tests.api.ApiBaseTests import ApiBaseTest


class CryptographyFernetTest(ApiBaseTest):
    def test_encrypt(self):
        # given
        crypt_fernet = CryptographyFernet()
        iterations = 480_000
        password = 'test'
        master_password = 'secret_master_password'

        # when
        password_encrypt = crypt_fernet.password_encrypt(message=password.encode(), password=master_password, iterations=iterations)

        # then
        assert password_encrypt
        assert type(password_encrypt) == bytes
        assert password_encrypt != password.encode()

    def test_encrypt_and_encrypt(self):
        # given
        crypt_fernet = CryptographyFernet()
        iterations = 480_000
        password = 'test'
        master_password = 'secret_master_password'

        # when - encrypt
        password_encrypt = crypt_fernet.password_encrypt(message=password.encode(), password=master_password, iterations=iterations)

        # then
        assert password_encrypt
        assert type(password_encrypt) == bytes
        assert password_encrypt != password

        # when - decrypt
        password_decrypt = crypt_fernet.password_decrypt(token=password_encrypt, password=master_password)
        assert password_decrypt
        assert type(password_decrypt) == bytes
        assert password_decrypt.decode() == password

    def test_encrypt_and_encrypt_very_long_password(self):
        # given
        crypt_fernet = CryptographyFernet()
        iterations = 480_000
        password = 'e0e85f3d3da8a678d9db1aeb9a3adb15ed61ca1b2d006cb74d3b7b994320d42490b7df26c0277e1b3c2bd9d1625992bfa307ab22d16c2101ab40d267ed16c713d5c5af2917bc0e4350de559d2a7b980b3a5063fa1ad8110d674014285dccfb66619ab704914a9eab7481ec7203846ae2e6f4a7c2ad5888d02d136c596447d630'
        master_password = 'secret_master_password'

        # when - encrypt
        password_encrypt = crypt_fernet.password_encrypt(message=password.encode(), password=master_password, iterations=iterations)

        # then
        assert password_encrypt
        assert type(password_encrypt) == bytes
        assert password_encrypt != password

        # when - decrypt
        password_decrypt = crypt_fernet.password_decrypt(token=password_encrypt, password=master_password)
        assert password_decrypt
        assert type(password_decrypt) == bytes
        assert password_decrypt.decode() == password

    def test_encrypt_and_encrypt_very_long_password_and_very_long_master_password(self):
        # given
        crypt_fernet = CryptographyFernet()
        iterations = 480_000
        password = 'e0e85f3d3da8a678d9db1aeb9a3adb15ed61ca1b2d006cb74d3b7b994320d42490b7df26c0277e1b3c2bd9d1625992bfa307ab22d16c2101ab40d267ed16c713d5c5af2917bc0e4350de559d2a7b980b3a5063fa1ad8110d674014285dccfb66619ab704914a9eab7481ec7203846ae2e6f4a7c2ad5888d02d136c596447d630'
        master_password = '8be327a0d7b1777bfa35b4522e074cd1d1f4cc9fc5abbfe7e2f3c253062154c3cd09104b4ad5ed8ce8d420e8c7b1e529713c008d150aca9dcc7d23edbe5d1534878a79626221a1777644f0814923931846324149c2573be1c3960adef2d2549e7694b690d77541028d57ec112cfe51b2f6945365d6a741272f889d1dcd904841'

        # when - encrypt
        password_encrypt = crypt_fernet.password_encrypt(message=password.encode(), password=master_password, iterations=iterations)

        # then
        assert password_encrypt
        assert type(password_encrypt) == bytes
        assert password_encrypt != password

        # when - decrypt
        password_decrypt = crypt_fernet.password_decrypt(token=password_encrypt, password=master_password)
        assert password_decrypt
        assert type(password_decrypt) == bytes
        assert password_decrypt.decode() == password
