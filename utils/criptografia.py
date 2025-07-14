from cryptography.fernet import Fernet

class Criptografia:
    def __init__(self):
        self.chave = Fernet.generate_key()
        self.cipher = Fernet(self.chave)

    def criptografar(self, dados):
        return self.cipher.encrypt(dados)

    def descriptografar(self, dados):
        return self.cipher.decrypt(dados)