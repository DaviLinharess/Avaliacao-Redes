# cliente.py

import socket
import psutil
import json
import time
import ssl


class Cliente:
    """
    Classe que representa o cliente da aplicação.
    Ele coleta dados do sistema e os envia para o servidor.
    """
    def __init__(self, host_servidor, port_servidor):
        """
        Construtor da classe Cliente.
        
        Args:
            host_servidor (str): Endereço de IP do servidor ao qual se conectar.
            port_servidor (int): Porta do servidor.
        """
        self.host_servidor = host_servidor
        self.port_servidor = port_servidor
        self.sock = None

    def connect(self):
        try:
            contexto = ssl.create_default_context()
            contexto.check_hostname = False
            contexto.verify_mode = ssl.CERT_NONE

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock = contexto.wrap_socket(sock, server_hostname=self.host_servidor)
            self.sock.connect((self.host_servidor, self.port_servidor))

            print(f"[*] Conectado com sucesso ao servidor {self.host_servidor}:{self.port_servidor}")
            return True
        except ConnectionRefusedError:
            print("[!] Conexão recusada. Verifique se o servidor está online e o IP/porta estão corretos.")
            return False
        except socket.gaierror:
            print(f"[!] Endereço do servidor '{self.host_servidor}' não encontrado.")
            return False

    def get_system_info(self):
        """Coleta diversas informações do sistema usando a biblioteca psutil."""
        print("Coletando informações do sistema...")
        # (0,5) - Quantidade de Processadores
        cpu_fisicos = psutil.cpu_count(logical=False)
        cpu_total = psutil.cpu_count(logical=True)
        
        # (0,5) - Memória RAM Livre
        memoria = psutil.virtual_memory()
        ram_livre_gb = round(memoria.free / (1024**3), 2)
        
        # (0,5) - Espaço em disco livre
        disco = psutil.disk_usage('/')
        disco_livre_gb = round(disco.free / (1024**3), 2)
        
        # (0,5) - Endereço IP das Interfaces e (0,5) Mostrar Interfaces Desativadas
        interfaces = self._get_network_info()

        # (0,5) - Listar portas TCP e UDP abertas (em modo de escuta)
        conexoes = psutil.net_connections(kind='inet')
        portas_tcp_listen = sorted(list(set([conn.laddr.port for conn in conexoes if conn.type == socket.SOCK_STREAM and conn.status == 'LISTEN'])))
        portas_udp = sorted(list(set([conn.laddr.port for conn in conexoes if conn.type == socket.SOCK_DGRAM])))

        # Monta o dicionário com todas as informações
        info = {
            "Processadores (Físicos)": cpu_fisicos,
            "Processadores (Total)": cpu_total,
            "Memória RAM Livre (GB)": ram_livre_gb,
            "Espaço em Disco Livre (GB)": disco_livre_gb,
            "Interfaces de Rede": interfaces,
            "Portas TCP Abertas (Listen)": portas_tcp_listen,
            "Portas UDP Abertas": portas_udp,
        }
        return info

    def _get_network_info(self):
        """Método auxiliar para obter informações detalhadas das interfaces de rede."""
        interfaces_info = {}
        stats = psutil.net_if_stats()
        addrs = psutil.net_if_addrs()

        for name, snicaddrs in addrs.items():
            status = "Ativa" if stats[name].isup else "Desativada"
            enderecos_ipv4 = []
            for snicaddr in snicaddrs:
                if snicaddr.family == socket.AF_INET:
                    enderecos_ipv4.append(snicaddr.address)
            
            # Só adiciona a interface se ela tiver um IP ou for relevante
            if enderecos_ipv4 or status == "Desativada":
                 interfaces_info[name] = {
                    "Status": status,
                    "Endereços IP": enderecos_ipv4 if enderecos_ipv4 else "N/A"
                }
        return interfaces_info
        
    def run(self, interval_seconds=10):
        """
        Método principal do cliente. Conecta e envia dados periodicamente.
        """
        if not self.connect():
            return # Se não conectar, encerra o script.
            
        try:
            while True:
                # Coleta os dados do sistema.
                data = self.get_system_info()
                
                # Serializa o dicionário Python para uma string JSON e a codifica para bytes.
                serialized_data = json.dumps(data).encode('utf-8')
                
                # Envia os dados para o servidor.
                self.sock.send(serialized_data)
                print(f"[*] Dados enviados com sucesso. Próximo envio em {interval_seconds} segundos.")
                
                # Espera o tempo definido antes de repetir o processo.
                time.sleep(interval_seconds)
        except (BrokenPipeError, ConnectionResetError):
            print("[!] A conexão com o servidor foi perdida. Encerrando cliente.")
        finally:
            # Garante que o socket seja fechado ao final.
            self.sock.close()
            print("[*] Conexão fechada.")

# --- Ponto de Entrada do Script ---
if __name__ == "__main__":
    # IMPORTANTE: Altere este IP para o endereço da máquina onde o servidor está rodando.
    # Se for na mesma máquina, use '127.0.0.1'.
    IP_DO_SERVIDOR = "127.0.0.1"
    PORTA_DO_SERVIDOR = 5000
    
    cliente = Cliente(IP_DO_SERVIDOR, PORTA_DO_SERVIDOR)
    cliente.run()