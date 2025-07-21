import socket
import ssl
import threading
import pickle

class ServidorSSL:
    def __init__(self, host="0.0.0.0", porta_tcp=5000, certfile="certificado.pem", keyfile="chave.pem"):
        self.host = host
        self.porta_tcp = porta_tcp
        self.certfile = certfile
        self.keyfile = keyfile
        self.clientes = {}  # { (ip, porta): {"socket": conexao, "dados": dados} }

    def iniciar(self):
        contexto_ssl = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        contexto_ssl.load_cert_chain(certfile=self.certfile, keyfile=self.keyfile)

        servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor_socket.bind((self.host, self.porta_tcp))
        servidor_socket.listen()
        print(f"[SERVIDOR SSL] Escutando em {self.host}:{self.porta_tcp}")

        servidor_ssl_socket = contexto_ssl.wrap_socket(servidor_socket, server_side=True)

        thread_aceitar = threading.Thread(target=self.aceitar_clientes, args=(servidor_ssl_socket,))
        thread_aceitar.daemon = True
        thread_aceitar.start()

        self.menu()

    def aceitar_clientes(self, servidor_ssl_socket):
        while True:
            cliente_ssl_socket, endereco = servidor_ssl_socket.accept()
            print(f"[NOVA CONEXÃO SSL] Cliente conectado: {endereco}")
            self.clientes[endereco] = {"socket": cliente_ssl_socket, "dados": None}

            thread = threading.Thread(target=self.tratar_cliente, args=(cliente_ssl_socket, endereco))
            thread.daemon = True
            thread.start()

    def tratar_cliente(self, cliente_ssl_socket, endereco):
        while True:
            try:
                dados_recebidos = cliente_ssl_socket.recv(4096)
                if not dados_recebidos:
                    break

                informacoes = pickle.loads(dados_recebidos)
                self.clientes[endereco]["dados"] = informacoes

            except:
                print(f"[DESCONECTADO] Cliente {endereco} foi desconectado")
                break

        cliente_ssl_socket.close()
        del self.clientes[endereco]

    def menu(self):
        while True:
            print("\n--- MENU SERVIDOR SSL ---")
            print("1 - Listar clientes conectados")
            print("2 - Detalhar cliente")
            print("3 - Mostrar médias dos dados")
            print("4 - Sair")
            opcao = input("Escolha uma opção: ")

            if opcao == "1":
                self.listar_clientes()
            elif opcao == "2":
                self.detalhar_cliente()
            elif opcao == "3":
                self.mostrar_medias()
            elif opcao == "4":
                print("Encerrando servidor SSL...")
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
            print("Nenhum dado recebido ainda.")

    def mostrar_medias(self):
        total_clientes = len(self.clientes)
        if total_clientes == 0:
            print("Nenhum cliente conectado.")
            return

        soma_ram = 0
        soma_disco = 0
        soma_portas = 0
        contagem = 0

        for info in self.clientes.values():
            dados = info["dados"]
            if dados:
                soma_ram += dados["memoria_ram_livre"]
                soma_disco += dados["espaco_disco_livre"]
                soma_portas += len(dados["portas_abertas"])
                contagem += 1

        if contagem == 0:
            print("Nenhum dado recebido ainda para calcular médias.")
            return

        media_ram = soma_ram / contagem
        media_disco = soma_disco / contagem
        media_portas = soma_portas / contagem

        print("\n--- MÉDIAS DOS DADOS COLETADOS ---")
        print(f"Média RAM Livre: {media_ram / (1024 ** 3):.2f} GB")
        print(f"Média Disco Livre: {media_disco / (1024 ** 3):.2f} GB")
        print(f"Média Número de Portas Abertas: {media_portas:.2f}")

