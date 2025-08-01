# servidor.py

import socket
import threading
import json

class Servidor:
    """
    Classe que representa o servidor da aplicação.
    Ele escuta por conexões de clientes e recebe dados de sistema.
    """
    def __init__(self, host='0.0.0.0', port=12345):
        """
        Construtor da classe Servidor.
        
        Args:
            host (str): Endereço de IP no qual o servidor irá escutar. '0.0.0.0' significa
                        que ele aceitará conexões de qualquer interface de rede.
            port (int): Porta na qual o servidor irá escutar.
        """
        self.host = host
        self.port = port
        self.clients = {}  # Dicionário para armazenar clientes: {addr: conn}
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # A opção SO_REUSEADDR permite que o servidor reinicie e use a mesma porta rapidamente.
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def start(self):
        """
        Inicia o servidor, coloca-o em modo de escuta e começa a aceitar conexões.
        """
        # Vincula o socket ao endereço e porta especificados.
        self.sock.bind((self.host, self.port))
        # Define o limite de conexões pendentes.
        self.sock.listen(5)
        print(f"[*] Servidor iniciado e escutando em {self.host}:{self.port}")

        # Loop principal para aceitar novas conexões.
        while True:
            # accept() é uma chamada bloqueante: o código para aqui até um cliente se conectar.
            # Retorna o objeto de conexão (conn) e o endereço (addr) do cliente.
            conn, addr = self.sock.accept()
            
            print(f"[*] Nova conexão aceita de {addr[0]}:{addr[1]}")
            self.clients[addr] = conn

            # Cria uma nova thread para gerenciar a comunicação com este cliente.
            # Isso permite que o servidor lide com múltiplos clientes simultaneamente.
            client_thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            client_thread.start()

    def handle_client(self, conn, addr):
        """
        Gerencia a comunicação com um cliente conectado.
        Esta função roda em uma thread separada para cada cliente.
        """
        print(f"[*] Iniciando comunicação com {addr[0]}")
        try:
            # Loop para receber dados do cliente continuamente.
            while True:
                # Espera por dados do cliente (buffer de 4096 bytes).
                data = conn.recv(4096)
                # Se não receber dados, significa que o cliente desconectou.
                if not data:
                    break
                
                # Decodifica os bytes para string e converte a string JSON para um dicionário Python.
                client_data = json.loads(data.decode('utf-8'))
                
                print("\n" + "="*50)
                print(f"Dados recebidos do cliente {addr[0]}:")
                # Usa json.dumps com indentação para imprimir os dados de forma legível.
                print(json.dumps(client_data, indent=4, ensure_ascii=False))
                print("="*50 + "\n")

        except ConnectionResetError:
            # Ocorre quando a conexão é fechada abruptamente pelo cliente.
            print(f"[!] A conexão com {addr[0]} foi perdida.")
        except json.JSONDecodeError:
            print(f"[!] Erro ao decodificar JSON do cliente {addr[0]}.")
        finally:
            # Garante que a conexão seja fechada e o cliente removido da lista.
            print(f"[*] Cliente {addr[0]} desconectado.")
            if addr in self.clients:
                del self.clients[addr]
            conn.close()

# --- Ponto de Entrada do Script ---
# Este bloco só é executado quando o arquivo é rodado diretamente (python servidor.py).
if __name__ == "__main__":
    servidor = Servidor()
    servidor.start()