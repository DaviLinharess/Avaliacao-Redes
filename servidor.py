import socket
import threading
import pickle #enviar dados como objeto Python
from utils.criptografia import Criptografia

class Servidor:
    def __init__(self, host="0.0.0.0", porta=5000):
        self.host = host
        self.porta = porta
        self.cliente = {} #{(ip, porta): conexao }
        self.cripto = Criptografia()

    def iniciar(self):
        servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor_socket.bind((self.host, self.porta))
        servidor_socket.listen()
        print(f"[SERVIDOR] Escutando em {self.host}:{self.porta}")

        while True:
            cliente_socket, endereco = servidor_socket.accept()
            print(f"[NOVA CONEXÃO] Cliente conectado: {endereco}")
            self.clientes[endereco] = cliente_socket

            thread = threading.Thread(target=self.tratar_cliente, args=(cliente_socket, endereco))
            thread.start()

    def tratar_cliente(self, cliente_socket, endereco):
        while True:
            try:
                dados_recebidos = cliente_socket.recv(4096)
                if not dados_recebidos:
                    break

                #pra decodificar e descriptografar dados
                dados = self.cripto.descriptografar(dados_recebidos)
                informacoes = pickle.loads(dados)

                print(f"[DADOS DE {endereco}]: {informacoes}")
            except:
                print(f"[DESCONECTADO] Cliente {endereco} foi desconectado")
                break
        
        cliente_socket.close()
        del self.cliente[endereco]

if __name__ == "__main__":
    servidor = Servidor()
    servidor.iniciar()
    