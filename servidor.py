import socket
import threading
import pickle
from utils.criptografia import Criptografia

class Servidor:
    def __init__(self, host="0.0.0.0", porta_tcp=5000, porta_udp=6000):
        self.host = host
        self.porta_tcp = porta_tcp
        self.porta_udp = porta_udp
        self.clientes = {}  # { (ip, porta): {"socket": conexao, "dados": dados} }
        self.cripto = Criptografia()

    def iniciar(self):
        # Inicia o listener UDP em uma thread separada
        thread_udp = threading.Thread(target=self.escutar_broadcast_udp)
        thread_udp.daemon = True
        thread_udp.start()

        # Inicia o servidor TCP
        servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor_socket.bind((self.host, self.porta_tcp))
        servidor_socket.listen()
        print(f"[SERVIDOR] Escutando TCP em {self.host}:{self.porta_tcp}")
        print(f"[SERVIDOR] Escutando UDP (descoberta) na porta {self.porta_udp}")

        thread_aceitar = threading.Thread(target=self.aceitar_clientes, args=(servidor_socket,))
        thread_aceitar.daemon = True
        thread_aceitar.start()

        self.menu()

    def escutar_broadcast_udp(self):
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.bind((self.host, self.porta_udp))

        while True:
            dados, endereco = udp_socket.recvfrom(1024)
            mensagem = dados.decode()
            print(f"[BROADCAST RECEBIDO] {mensagem} de {endereco}")

    def aceitar_clientes(self, servidor_socket):
        while True:
            cliente_socket, endereco = servidor_socket.accept()
            print(f"[NOVA CONEXÃO] Cliente conectado: {endereco}")
            self.clientes[endereco] = {"socket": cliente_socket, "dados": None}

            thread = threading.Thread(target=self.tratar_cliente, args=(cliente_socket, endereco))
            thread.daemon = True
            thread.start()

    def tratar_cliente(self, cliente_socket, endereco):
        while True:
            try:
                dados_recebidos = cliente_socket.recv(4096)
                if not dados_recebidos:
                    break

                dados = self.cripto.descriptografar(dados_recebidos)
                informacoes = pickle.loads(dados)
                self.clientes[endereco]["dados"] = informacoes

            except:
                print(f"[DESCONECTADO] Cliente {endereco} foi desconectado")
                break

        cliente_socket.close()
        del self.clientes[endereco]

    def menu(self):
        while True:
            print("\n--- MENU SERVIDOR ---")
            print("1 - Listar clientes conectados")
            print("2 - Detalhar cliente")
            print("3 - Sair")
            opcao = input("Escolha uma opção: ")

            if opcao == "1":
                self.listar_clientes()
            elif opcao == "2":
                self.detalhar_cliente()
            elif opcao == "3":
                print("Encerrando servidor...")
                break
            else:
                print("Opção inválida.")

    def listar_clientes(self):
        if not self.clientes:
            print("Nenhum cliente conectado.")
            return
        print("\n--- CLIENTES CONECTADOS ---")
        for idx, (endereco, _) in enumerate(self.clientes.items()):
            print(f"{idx + 1}. {endereco}")

    def detalhar_cliente(self):
        if not self.clientes:
            print("Nenhum cliente conectado.")
            return

        self.listar_clientes()
        escolha = int(input("Escolha o número do cliente: ")) - 1
        if escolha < 0 or escolha >= len(self.clientes):
            print("Cliente inválido.")
            return

        endereco = list(self.clientes.keys())[escolha]
        dados = self.clientes[endereco]["dados"]

        if dados:
            print(f"\n--- DADOS DE {endereco} ---")
            for chave, valor in dados.items():
                print(f"{chave}: {valor}")
        else:
            print("Nenhumm dado recebido.")
