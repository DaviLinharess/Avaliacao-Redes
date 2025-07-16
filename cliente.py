import socket
import ssl
import pickle
import time
from utils.coleta_dados import coletar_dados

class ClienteSSL:
    def __init__(self, servidor_host="127.0.0.1", servidor_porta_tcp=5000, certfile="certificado.pem"):
        self.servidor_host = servidor_host
        self.servidor_porta_tcp = servidor_porta_tcp
        self.certfile = certfile

    def conectar(self):
        contexto_ssl = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        contexto_ssl.check_hostname = False
        contexto_ssl.verify_mode = ssl.CERT_NONE  #ignora validação de certificado para testes

        cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cliente_ssl_socket = contexto_ssl.wrap_socket(cliente_socket, server_hostname=self.servidor_host)

        cliente_ssl_socket.connect((self.servidor_host, self.servidor_porta_tcp))
        print("[CLIENTE SSL] Conectado ao servidor")

        try:
            while True:
                dados = coletar_dados()
                dados_serializados = pickle.dumps(dados)
                cliente_ssl_socket.sendall(dados_serializados)
                print("[CLIENTE SSL] Dados enviados ao servidor")
                time.sleep(5)
        except KeyboardInterrupt:
            print("\n[CLIENTE SSL] Desconectando...")
            cliente_ssl_socket.close()

if __name__ == "__main__":
    cliente = ClienteSSL()
    cliente.conectar()
