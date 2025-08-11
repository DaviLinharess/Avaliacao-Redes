import socket
import psutil
import json
import time
import ssl


class Cliente: #coleta dados do sistema e os envia pro servidor.
    def __init__(self, host_servidor, port_servidor):
                        #host_servidor: Endereço de IP do servidor ao qual se conectar.
                        #port_servidor: Porta do servidor.
        self.host_servidor = host_servidor
        self.port_servidor = port_servidor
        self.sock = None

    def connect(self):
        try:
            contexto = ssl.create_default_context() #criptografia
            contexto.check_hostname = False         #desativa a verificação do certificado de segurança
            contexto.verify_mode = ssl.CERT_NONE    

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                        # cria o socket em IPv4 e protocolo TCP
            self.sock = contexto.wrap_socket(sock, server_hostname=self.host_servidor)      # pega o sock (TCP normal) e coloca as config de segurança 
            self.sock.connect((self.host_servidor, self.port_servidor))                     # tenta conectar ao IP e a porta do servidor

            print(f"[*] Conectado com sucesso ao servidor {self.host_servidor}:{self.port_servidor}")
            return True
        except ConnectionRefusedError:                                                      # erro se o servidor tiver off
            print("[!] Erro, veja se o servidor está online ou a porta ta certa.")
            return False
        except socket.gaierror:                                                             # enderaço IP errado
            print(f"[!] Endereço do servidor '{self.host_servidor}' não existe.")
            return False

    def get_system_info(self):                                                              #pega informações do sistema do o psutil
        print("Coletando informações do sistema...")
                                                        # Qnt de processadores
        cpu_fisicos = psutil.cpu_count(logical=False)
        cpu_total = psutil.cpu_count(logical=True)
        
                                                        # Memória RAM livre
        memoria = psutil.virtual_memory()
        ram_livre_gb = round(memoria.free / (1024**3), 2)
        
                                                        # Espaço do disco livre
        disco = psutil.disk_usage('/')
        disco_livre_gb = round(disco.free / (1024**3), 2)
        
                                                        # Endereço IP das interfaces e mostrar as desativadas
        interfaces = self._get_network_info()

                                                        # Listar portas TCP e UDP abertas (em escuta)
        conexoes = psutil.net_connections(kind='inet')
        portas_tcp_listen = sorted(list(set([conn.laddr.port for conn in conexoes if conn.type == socket.SOCK_STREAM and conn.status == 'LISTEN'])))
        portas_udp = sorted(list(set([conn.laddr.port for conn in conexoes if conn.type == socket.SOCK_DGRAM])))

                                                        # Dic com todas as informações
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

    def _get_network_info(self):                         # pegar informações das placas de rede
        interfaces_info = {}
        stats = psutil.net_if_stats()
        addrs = psutil.net_if_addrs()

        for name, snicaddrs in addrs.items():                                               # pra cada uma, itinera por todas interfaces encontradas pelo psutil
            status = "Ativa" if stats[name].isup else "Desativada"                          # verifica os status
            enderecos_ipv4 = []                                                             # procura por endereços IPv4 associados a ela
            for snicaddr in snicaddrs:          
                if snicaddr.family == socket.AF_INET:                                          
                    enderecos_ipv4.append(snicaddr.address)                                 #adiciona tudo numa bibllioteca
            
                                                                                            # Só adiciona na biblioteca se ela tiver um IP
            if enderecos_ipv4 or status == "Desativada":
                 interfaces_info[name] = {
                    "Status": status,
                    "Endereços IP": enderecos_ipv4 if enderecos_ipv4 else "N/A"
                }
        return interfaces_info
        
    def run(self, interval_seconds=10):                 # Conecta e envia dados de 10 em 10 seg

        if not self.connect():
            return                                      # Se não conectar, encerra.
            
        try:
            while True:
                                                        # Coleta de dados mais recentes.
                data = self.get_system_info()
                
                                                        # converte o dicionario "data" em string no formado do "JSON"
                                                        # depois, converte o "JSON" em bytes padrão utf-8, pq os soquetes n enviam
                                                        # strings, e sim bytes.
                serialized_data = json.dumps(data).encode('utf-8')
                
                                                        # envia esses bytes pro servidor.
                self.sock.send(serialized_data)
                print(f"[*] Dados enviados com sucesso. Próximo envio em {interval_seconds} segundos.")
                
                                                        # espera 10seg pra reiniciar.
                time.sleep(interval_seconds)

        except (BrokenPipeError, ConnectionResetError):
            print("[!] Conexão perdida. Encerrando cliente.")
                

        finally:
            # garante que o sock.close seja chamado.
            # fecha a conexão e libera os recursos do sistema
            self.sock.close()
            print("[*] Conexão fechada.")



    #executar
if __name__ == "__main__":
    # defini as constantes: IP 127.0.0.1 e porta 5000
    # Se for na mesma máquina, use '127.0.0.1'.
    IP_DO_SERVIDOR = "127.0.0.1"
    PORTA_DO_SERVIDOR = 5000
    
    #objeto da classe Cliente, fornecendo o IP e porta
    cliente = Cliente(IP_DO_SERVIDOR, PORTA_DO_SERVIDOR)
    cliente.run() 