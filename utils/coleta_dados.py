import psutil
import socket

def coletar_dados():
    dados = {
        "cpu_count": psutil.cpu_count(),
        "memoria_ram_livre": psutil.virtual_memory().available,
        "espaco_disco_livre": psutil.disk_usage("/").free,
        "enderecos_ip": [i.address for i in psutil.net_if_addrs()['lo']],
        "portas_abertas": listar_portas_abertas(),
    }
    return dados

def listar_portas_abertas():
    portas = []
    conexoes = psutil.net_connections()
    for c in conexoes:
        if c.status == "LISTEN":
            portas.append({"tipo": c.type, "porta": c.laddr.port})
    return portas
