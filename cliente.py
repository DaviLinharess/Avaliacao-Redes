import socket
import pickle
import time
from utils.coleta_dados import coletar_dados
from utils.criptografia import Criptografia

class Cliente:
    def __init__(self, servidor_porta_tcp=5000, servidor_porta_udp=6000):
        self.servidor_porta_tcp = servidor_porta_tcp
        self.servidor_porta_udp = servidor_porta_udp
        self.cripto = Criptografia()

    def enviar_broadcast_udp(self):
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        mensagem = "Cliente online"
        udp_socket.sendto(mensagem.encode(), ('<broadcast>', self.servidor_porta_udp))
        print("[CLIENTE] Broadcast UDP enviado")

    def conectar(self, servidor_host):
        cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cliente_socket.connect((servidor_host, self.servidor_porta_tcp))
        print("[CLIENTE] Conectado ao servidor")

        try:
            while True:
                dados = coletar_dados()
                dados_serializados = pickle.dumps(dados)
                dados_criptografados = self.cripto.criptografar(dados_serializados)

                cliente_socket.sendall(dados_criptografados)
                print("[CLIENTE] Dados enviados ao servidor")
                time.sleep(5)
        except KeyboardInterrupt:
            print("\n[CLIENTE] Desconectando...")
            cliente_socket.close()

if __name__ == "__main__":
    cliente = Cliente()
    cliente.enviar_broadcast_udp()
    servidor_host = input("Digite o IP do servidor TCP (ou pressione Enter para 127.0.0.1): ") or "127.0.0.1"
    cliente.conectar(servidor_host)
