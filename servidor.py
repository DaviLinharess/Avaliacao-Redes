import socket
import ssl
import threading
import json

class Servidor:
    def __init__(self, host="0.0.0.0", porta_tcp=5000, certfile="certificado.pem", keyfile="chave.pem"):
        self.host = host
        self.porta_tcp = porta_tcp
        self.certfile = certfile
        self.keyfile = keyfile
        self.clientes = {}  # {endereco: {"conexao": conexao, "dados": dados}}

    def iniciar(self):
        contexto_ssl = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        contexto_ssl.load_cert_chain(certfile=self.certfile, keyfile=self.keyfile)

        servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor_socket.bind((self.host, self.porta_tcp))
        servidor_socket.listen(5)

        print(f"[SERVIDOR SSL] Escutando em {self.host}:{self.porta_tcp}...\n")

        servidor_ssl_socket = contexto_ssl.wrap_socket(servidor_socket, server_side=True)

        while True:
            conexao, endereco = servidor_ssl_socket.accept()
            print(f"[NOVA CONEXÃO] Cliente conectado: {endereco}")
            thread = threading.Thread(target=self._lidar_com_cliente, args=(conexao, endereco))
            thread.start()

    def _lidar_com_cliente(self, conexao, endereco):
        try:
            while True:
                dados_recebidos = conexao.recv(4096).decode("utf-8")
                if not dados_recebidos:
                    break

                dados_json = json.loads(dados_recebidos)

                # Atualiza ou registra os dados do cliente
                self.clientes[endereco] = {
                    "conexao": conexao,
                    "dados": dados_json
                }

                print(f"[DADOS RECEBIDOS] de {endereco}: {dados_json}")
        except Exception as e:
            print(f"[ERRO] {e}")
        finally:
            conexao.close()
            print(f"[!] Conexão com {endereco} encerrada.")

        
    def listar_clientes(self):
        if not self.clientes:
            print("Nenhum cliente conectado.")
        else:
            for i, (endereco, info) in enumerate(self.clientes.items(), 1):
                print(f"{i}. {endereco} - CPUs Totais: {info['dados'].get('Processadores (Total)', 'Desconhecido')} núcleos")
                

    def detalhar_cliente(self):
        if not self.clientes:
            print("Nenhum cliente conectado.")
            return

        self.listar_clientes()
        try:
            escolha = int(input("Escolha o número do cliente: "))
        except ValueError:
            print("Opção inválida: deve ser um número.")
            return
        
        if escolha < 1 or escolha > len(self.clientes):
            print("Opção inválida: cliente não existe.")
            return

        endereco = list(self.clientes.keys())[escolha - 1]
        dados = self.clientes[endereco]["dados"]

        print("\n===== Detalhes do Cliente =====")
        print(f"CPUs Totais: {dados.get('Processadores (Total)', 'Desconhecido')} núcleos")
        print(f"Memória RAM Livre: {dados.get('Memória RAM Livre (GB)', 'Desconhecido')} GB")
        print(f"Espaço em Disco Livre: {dados.get('Espaço em Disco Livre (GB)', 'Desconhecido')} GB")

        print("\n--- Interfaces de Rede ---")
        interfaces = dados.get("Interfaces de Rede", {})
        for nome, info in interfaces.items():
            status = info.get("Status", "Desconhecido")
            ips = info.get("Endereços IP", [])
            if isinstance(ips, list):
                ips = ", ".join(ips) if ips else "Sem IP"
            print(f"{nome} - {status} - IPs: {ips}")

        print("\n--- Portas Abertas ---")
        portas_tcp = dados.get("Portas TCP Abertas (Listen)", [])
        portas_udp = dados.get("Portas UDP Abertas", [])
        print(f"TCP: {', '.join(map(str, portas_tcp)) if portas_tcp else 'Nenhuma'}")
        print(f"UDP: {', '.join(map(str, portas_udp)) if portas_udp else 'Nenhuma'}")
        
    def menu(self):
        while True:
            print("\n===== MENU SERVIDOR =====")
            print("1. Listar clientes")
            print("2. Detalhar cliente")
            print("3. Ver média dos dados recebidos")
            print("0. Sair")

            opcao = input("Escolha uma opção: ")

            if opcao == "1":
                self.listar_clientes()
            elif opcao == "2":
                self.detalhar_cliente()
            elif opcao == "3":
                self.calcular_media_dos_dados()
            elif opcao == "0":
                print("Encerrando servidor...")
                break
            else:
                print("Opção inválida.")


    def calcular_media_dos_dados(self):
        if not self.clientes:
            print("[!] Nenhum cliente conectado.")
            return

        total = 0
        soma_ram = soma_disco = soma_cpu = 0

        for cliente_id, cliente in self.clientes.items():
            dados = cliente.get("dados", {})
            try:
                soma_ram += dados["Memória RAM Livre (GB)"]
                soma_disco += dados["Espaço em Disco Livre (GB)"]
                soma_cpu += dados["Processadores (Total)"]
                total += 1
            except KeyError:
                print(f"[!] Dados incompletos do cliente {cliente_id}. Ignorando...")
                continue

        if total == 0:
            print("[!] Nenhum cliente com dados completos para cálculo.")
            return

        media_ram = round(soma_ram / total, 2)
        media_disco = round(soma_disco / total, 2)
        media_cpu = round(soma_cpu / total, 2)

        print("\n==== MÉDIAS DOS DADOS RECEBIDOS ====")
        print(f"Média RAM Livre: {media_ram} GB")
        print(f"Média Disco Livre: {media_disco} GB")
        print(f"Média de CPUs (total): {media_cpu}")

if __name__ == "__main__":
    servidor = Servidor()
    threading.Thread(target=servidor.iniciar, daemon=True).start()
    servidor.menu()