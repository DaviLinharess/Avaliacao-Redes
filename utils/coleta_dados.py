import psutil
import socket

def coletar_dados():
    # dados básicos
    dados = {
        "cpu_count": psutil.cpu_count(),
        "memoria_ram_livre": psutil.virtual_memory().available,
        "espaco_disco_livre": psutil.disk_usage("/").free,
        "enderecos_ip": {},
        "interfaces_desativadas": [],
        "portas_abertas": listar_portas_abertas(),
    }

    # endereços IP por interface
    for interface, addrs in psutil.net_if_addrs().items():
        ips = [addr.address for addr in addrs if addr.family == socket.AF_INET]
        dados["enderecos_ip"][interface] = ips

    # interfaces desativadas
    for interface, stats in psutil.net_if_stats().items():
        if not stats.isup:
            dados["interfaces_desativadas"].append(interface)

    return dados

def listar_portas_abertas():
    portas = []
    conexoes = psutil.net_connections()
    for c in conexoes:
        if c.status == "LISTEN":
            tipo = "TCP" if c.type == socket.SOCK_STREAM else "UDP"
            portas.append({"tipo": tipo, "porta": c.laddr.port})
    return portas
